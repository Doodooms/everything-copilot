"""Run-local Codex metrics capture used by the Plugin Factory Pilot A."""

from __future__ import annotations

import hmac
import http.server
import json
import os
import secrets
import threading
import uuid
from collections.abc import Mapping
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from expertise.validator import load_json_no_duplicate_keys

from .errors import HarnessFactoryError

_METRICS_PATH = "/v1/metrics"
_MAX_REQUEST_BYTES = 1_048_576
_MAX_CAPTURE_BYTES = 4_194_304


class PilotACodexMetricsCapture:
    """Capture authenticated OTLP/HTTP JSON metrics on an ephemeral loopback port.

    The receiver does not claim exporter completeness. It records each accepted raw
    OTLP JSON body in a private per-run file so Pilot A can pass the decoded mappings
    to its Codex event observer. Its endpoint and bearer token exist only for one run.
    """

    def __init__(self, state_directory: Path):
        self.state_directory = Path(state_directory)
        self._evidence_paths: list[Path] = []
        self.metadata_path = self.state_directory / "codex-metrics-capture.json"
        self.capture_id = uuid.uuid4().hex
        self.token = secrets.token_urlsafe(32)
        self._server: http.server.ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._captured_bytes = 0
        self._accepted_payloads = 0
        self._rejected_payloads = 0

    def __enter__(self) -> Self:
        if self.state_directory.is_symlink() or not self.state_directory.is_dir():
            raise HarnessFactoryError("Codex capture state directory must be regular")
        if (
            self.metadata_path.exists()
            or self.metadata_path.is_symlink()
            or any(self.state_directory.glob("codex-metrics-*.json"))
        ):
            raise HarnessFactoryError("Codex capture evidence path already exists")

        owner = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def setup(self) -> None:
                self.request.settimeout(2)
                super().setup()

            def log_message(self, format: str, *args: Any) -> None:
                return

            def _respond(self, status: int) -> None:
                self.send_response(status)
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True

            def _reject_payload(self, status: int) -> None:
                with owner._lock:
                    owner._rejected_payloads += 1
                self._respond(status)

            def do_POST(self) -> None:
                if self.path != _METRICS_PATH:
                    self._respond(404)
                    return
                expected = f"Bearer {owner.token}"
                provided = self.headers.get("Authorization", "")
                if not hmac.compare_digest(provided, expected):
                    self._respond(401)
                    return
                content_type = self.headers.get("Content-Type", "")
                media_type, *parameters = content_type.split(";")
                if media_type.strip().lower() != "application/json" or any(
                    parameter.strip().lower()
                    not in {"charset=utf-8", 'charset="utf-8"'}
                    for parameter in parameters
                ):
                    self._reject_payload(415)
                    return
                if self.headers.get("Transfer-Encoding") is not None:
                    self._reject_payload(400)
                    return
                try:
                    content_length = int(self.headers.get("Content-Length", ""))
                except ValueError:
                    self._reject_payload(400)
                    return
                if content_length <= 0:
                    self._reject_payload(400)
                    return
                if content_length > _MAX_REQUEST_BYTES:
                    self._reject_payload(413)
                    return
                body = self.rfile.read(content_length)
                if len(body) != content_length:
                    self._reject_payload(400)
                    return
                try:
                    payload = load_json_no_duplicate_keys(body)
                    _validate_otlp_payload(payload)
                except (ValueError, TypeError, UnicodeDecodeError):
                    self._reject_payload(400)
                    return

                with owner._lock:
                    if owner._captured_bytes + len(body) > _MAX_CAPTURE_BYTES:
                        owner._rejected_payloads += 1
                        self._respond(413)
                        return
                    evidence_path = owner.state_directory / (
                        f"codex-metrics-{owner._accepted_payloads + 1:04d}.json"
                    )
                    try:
                        descriptor = os.open(
                            evidence_path,
                            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                            0o600,
                        )
                    except OSError:
                        owner._rejected_payloads += 1
                        self._respond(500)
                        return
                    try:
                        _write_all(descriptor, body)
                    except OSError:
                        owner._evidence_paths.append(evidence_path)
                        owner._rejected_payloads += 1
                        self._respond(500)
                        return
                    finally:
                        os.close(descriptor)
                    owner._evidence_paths.append(evidence_path)
                    owner._captured_bytes += len(body)
                    owner._accepted_payloads += 1
                self._respond(200)

            def do_GET(self) -> None:
                self._respond(405)

            def do_PUT(self) -> None:
                self._respond(405)

        try:
            self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            self._server.daemon_threads = False
            self._thread = threading.Thread(
                target=self._server.serve_forever,
                kwargs={"poll_interval": 0.05},
                name="pilot-a-codex-metrics",
                daemon=True,
            )
            self._thread.start()
        except OSError as exc:
            raise HarnessFactoryError("Codex capture listener could not start") from exc
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        self._write_metadata()

    @property
    def endpoint(self) -> str:
        if self._server is None:
            raise HarnessFactoryError("Codex capture listener is not running")
        host, port = self._server.server_address[:2]
        if host != "127.0.0.1":
            raise HarnessFactoryError("Codex capture listener escaped loopback")
        return f"http://127.0.0.1:{port}{_METRICS_PATH}"

    @property
    def authorization_header(self) -> str:
        return f"Bearer {self.token}"

    @property
    def accepted_payloads(self) -> int:
        return self._accepted_payloads

    @property
    def raw_reference(self) -> str:
        return ",".join(str(path) for path in self._evidence_paths)

    @property
    def evidence_paths(self) -> tuple[Path, ...]:
        with self._lock:
            return tuple(self._evidence_paths)

    @property
    def artifact_paths(self) -> tuple[Path, ...]:
        paths = self.evidence_paths
        if self.metadata_path.is_file() and not self.metadata_path.is_symlink():
            return (*paths, self.metadata_path)
        return paths

    def codex_config_line(self) -> str:
        """Return the only opt-in Codex telemetry setting for this run."""
        endpoint = json.dumps(self.endpoint)
        authorization = json.dumps(self.authorization_header)
        return (
            "[otel]\n"
            "metrics_exporter = { otlp-http = { "
            f'endpoint = {endpoint}, protocol = "json", '
            f"headers = {{ Authorization = {authorization} }} }} }}\n"
        )

    def _write_metadata(self) -> None:
        if self.metadata_path.exists() or self.metadata_path.is_symlink():
            raise HarnessFactoryError("Codex capture metadata path already exists")
        status = "partial" if self._rejected_payloads else "unknown"
        document = {
            "schema_version": 1,
            "capture_id": self.capture_id,
            "capture_contract": {
                "capture_id": self.capture_id,
                "status": status,
                "dropped_data_points": None,
                "stream_closed": True,
            },
            "accepted_payloads": self._accepted_payloads,
            "rejected_payloads": self._rejected_payloads,
            "raw_references": [str(path) for path in self.evidence_paths],
        }
        try:
            descriptor = os.open(
                self.metadata_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except OSError as exc:
            raise HarnessFactoryError(
                "Codex capture metadata could not be created"
            ) from exc
        try:
            _write_all(
                descriptor,
                (
                    json.dumps(document, sort_keys=True, ensure_ascii=False) + "\n"
                ).encode("utf-8"),
            )
        finally:
            os.close(descriptor)


def read_codex_metrics_evidence(
    path: Path | tuple[Path, ...] | list[Path],
) -> list[dict[str, Any]]:
    """Load captured OTLP JSON records for `observe_codex_events` consumers."""
    paths = (path,) if isinstance(path, Path) else tuple(path)
    payloads: list[dict[str, Any]] = []
    for evidence_path in paths:
        if evidence_path.is_symlink() or not evidence_path.is_file():
            raise HarnessFactoryError(
                "Codex metrics evidence path must be a regular file"
            )
        try:
            payload = load_json_no_duplicate_keys(evidence_path.read_bytes())
            _validate_otlp_payload(payload)
        except (ValueError, TypeError, UnicodeDecodeError) as exc:
            raise HarnessFactoryError(
                f"Codex metrics evidence is invalid: {evidence_path.name}"
            ) from exc
        payloads.append(payload)
    return payloads


def _validate_otlp_payload(payload: Any) -> None:
    if not isinstance(payload, Mapping):
        raise TypeError("OTLP payload must be an object")
    resource_metrics = payload.get("resourceMetrics")
    if not isinstance(resource_metrics, list):
        raise TypeError("OTLP payload must contain resourceMetrics")
    for resource_metric in resource_metrics:
        if not isinstance(resource_metric, Mapping):
            raise TypeError("OTLP resource metric must be an object")
        scope_metrics = resource_metric.get("scopeMetrics")
        if not isinstance(scope_metrics, list):
            raise TypeError("OTLP resource metric must contain scopeMetrics")
        for scope_metric in scope_metrics:
            if not isinstance(scope_metric, Mapping):
                raise TypeError("OTLP scope metric must be an object")
            metrics = scope_metric.get("metrics")
            if not isinstance(metrics, list):
                raise TypeError("OTLP scope metric must contain metrics")
            for metric in metrics:
                if not isinstance(metric, Mapping) or not isinstance(
                    metric.get("name"), str
                ):
                    raise TypeError("OTLP metric must have a name")
                if metric["name"] != "codex.skill.injected":
                    continue
                total = metric.get("sum")
                if not isinstance(total, Mapping) or not isinstance(
                    total.get("dataPoints"), list
                ):
                    raise TypeError("Codex skill metric must contain sum dataPoints")
                for point in total["dataPoints"]:
                    if not isinstance(point, Mapping):
                        raise TypeError(
                            "Codex skill metric data point must be an object"
                        )
                    attributes = point.get("attributes")
                    if not isinstance(attributes, list):
                        raise TypeError(
                            "Codex skill metric data point must have attributes"
                        )
                    values: dict[str, str] = {}
                    for attribute in attributes:
                        if not isinstance(attribute, Mapping):
                            raise TypeError("OTLP metric attribute must be an object")
                        key = attribute.get("key")
                        value = attribute.get("value")
                        if not isinstance(key, str) or not isinstance(value, Mapping):
                            raise TypeError("OTLP metric attribute is malformed")
                        string_value = value.get("stringValue")
                        if key in {"skill", "invoke_type"} and not isinstance(
                            string_value, str
                        ):
                            raise TypeError(
                                f"Codex skill metric attribute {key!r} must be a string"
                            )
                        if isinstance(string_value, str):
                            values[key] = string_value
                    if not values.get("skill", "").strip():
                        raise ValueError(
                            "Codex skill metric data point must name a skill"
                        )


def _write_all(descriptor: int, content: bytes) -> None:
    view = memoryview(content)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short write while persisting Codex evidence")
        view = view[written:]
