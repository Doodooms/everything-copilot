const vscode = require("vscode");

const OUTPUT_CHANNEL_NAME = "Agentic Workflow Tool Snapshot";
const SNAPSHOT_FILE_NAME = "copilot-tools.snapshot.json";
const AUTO_EXPORT_INITIAL_DELAY_MS = 1500;
const AUTO_EXPORT_STABILIZATION_DELAY_MS = 500;
const AUTO_EXPORT_STABILIZATION_ATTEMPTS = 6;
const AUTO_EXPORT_DEBOUNCE_MS = 750;

function activate(context) {
    const outputChannel = vscode.window.createOutputChannel(OUTPUT_CHANNEL_NAME);
    context.subscriptions.push(outputChannel);

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "agenticWorkflow.exportLanguageModelToolsSnapshot",
            async () => {
                await runSafely(outputChannel, async () => {
                    const workspaceFolder = await pickWorkspaceFolder();
                    if (!workspaceFolder) {
                        return;
                    }

                    const snapshot = collectToolSnapshot([workspaceFolder]);
                    const snapshotUri = await writeSnapshotFile(workspaceFolder, snapshot);

                    writeSnapshotSummary(outputChannel, snapshot, snapshotUri);

                    const action = await vscode.window.showInformationMessage(
                        `Exported ${snapshot.toolCount} tools to ${snapshotUri.fsPath}`,
                        "Open Snapshot",
                        "Show Output"
                    );

                    if (action === "Open Snapshot") {
                        await vscode.window.showTextDocument(snapshotUri);
                    } else if (action === "Show Output") {
                        outputChannel.show(true);
                    }
                });
            }
        ),
        vscode.commands.registerCommand(
            "agenticWorkflow.checkLanguageModelToolName",
            async (toolName) => {
                await runSafely(outputChannel, async () => {
                    const candidateName = typeof toolName === "string"
                        ? toolName.trim()
                        : await vscode.window.showInputBox({
                            prompt: "Enter the exact Copilot tool or toolset name to check",
                            placeHolder: "Examples: search/codebase, search, vscode_askQuestions",
                            ignoreFocusOut: true,
                        });

                    if (!candidateName) {
                        return;
                    }

                    const snapshot = collectToolSnapshot();
                    const exactTool = snapshot.tools.find((tool) => tool.name === candidateName);
                    const exactToolSet = snapshot.toolSets.find((toolSet) => toolSet.name === candidateName);
                    const suggestions = findSuggestions(candidateName, snapshot);

                    outputChannel.clear();
                    outputChannel.appendLine(`Query: ${candidateName}`);
                    outputChannel.appendLine("");

                    if (exactTool) {
                        outputChannel.appendLine("Exact tool match found.");
                        outputChannel.appendLine(JSON.stringify(exactTool, null, 2));
                        outputChannel.show(true);
                        await vscode.window.showInformationMessage(`Exact tool found: ${candidateName}`);
                        return;
                    }

                    if (exactToolSet) {
                        outputChannel.appendLine("Exact toolset match found.");
                        outputChannel.appendLine(JSON.stringify(exactToolSet, null, 2));
                        outputChannel.show(true);
                        await vscode.window.showInformationMessage(`Exact toolset found: ${candidateName}`);
                        return;
                    }

                    outputChannel.appendLine("No exact match found.");
                    if (suggestions.length > 0) {
                        outputChannel.appendLine("");
                        outputChannel.appendLine("Closest matches:");
                        for (const suggestion of suggestions) {
                            outputChannel.appendLine(`- ${suggestion.kind}: ${suggestion.name}`);
                        }
                    }

                    outputChannel.show(true);
                    await vscode.window.showWarningMessage(
                        `No exact tool or toolset named '${candidateName}' was found.`
                    );
                });
            }
        )
    );

    registerAutomaticSnapshotRefresh(context, outputChannel);
}

function deactivate() {}

async function runSafely(outputChannel, callback) {
    try {
        await callback();
    } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`Error: ${message}`);
        outputChannel.show(true);
        await vscode.window.showErrorMessage(message);
    }
}

function collectToolSnapshot(workspaceFolders = []) {
    const tools = getLanguageModelTools()
        .map(serializeTool)
        .sort((left, right) => left.name.localeCompare(right.name));

    return {
        schemaVersion: 1,
        generatedAt: new Date().toISOString(),
        workspaceFolder: workspaceFolders[0] ? workspaceFolders[0].uri.fsPath : null,
        workspaceFolders: workspaceFolders.map((workspaceFolder) => workspaceFolder.uri.fsPath),
        _method: "runtime-vscode-lm-tools",
        toolCount: tools.length,
        tools,
        toolSets: buildToolSets(tools),
    };
}

function getLanguageModelTools() {
    if (!vscode.lm || !vscode.lm.tools) {
        throw new Error("vscode.lm.tools is not available in this VS Code build.");
    }

    return Array.from(vscode.lm.tools);
}

function serializeTool(tool) {
    const tags = Array.from(tool.tags || []).filter(Boolean).sort();
    const prefix = tool.name.includes("/") ? tool.name.split("/")[0] : null;

    return {
        name: tool.name,
        description: tool.description || "",
        tags,
        prefix,
        inputSchema: tool.inputSchema || null,
    };
}

function buildToolSets(tools) {
    const groups = new Map();

    for (const tool of tools) {
        if (tool.prefix) {
            addToolSetMember(groups, tool.prefix, tool.name, "name-prefix");
        }

        for (const tag of tool.tags) {
            addToolSetMember(groups, tag, tool.name, "tag");
        }
    }

    return Array.from(groups.entries())
        .filter(([, group]) => group.members.size > 1)
        .map(([name, group]) => ({
            name,
            members: Array.from(group.members).sort(),
            sources: Array.from(group.sources).sort(),
        }))
        .sort((left, right) => left.name.localeCompare(right.name));
}

function addToolSetMember(groups, toolSetName, toolName, source) {
    if (!toolSetName) {
        return;
    }

    const entry = groups.get(toolSetName) || {
        members: new Set(),
        sources: new Set(),
    };

    entry.members.add(toolName);
    entry.sources.add(source);
    groups.set(toolSetName, entry);
}

function findSuggestions(query, snapshot) {
    const normalizedQuery = query.toLowerCase();
    const ranked = [];

    for (const tool of snapshot.tools) {
        ranked.push({
            kind: "tool",
            name: tool.name,
            score: scoreNameMatch(normalizedQuery, tool.name.toLowerCase()),
        });
    }

    for (const toolSet of snapshot.toolSets) {
        ranked.push({
            kind: "toolset",
            name: toolSet.name,
            score: scoreNameMatch(normalizedQuery, toolSet.name.toLowerCase()),
        });
    }

    return ranked
        .filter((item) => item.score > 0)
        .sort((left, right) => right.score - left.score || left.name.localeCompare(right.name))
        .slice(0, 10)
        .map(({ kind, name }) => ({ kind, name }));
}

function scoreNameMatch(query, candidate) {
    if (candidate === query) {
        return 100;
    }

    if (candidate.startsWith(query)) {
        return 80;
    }

    if (candidate.includes(query)) {
        return 60;
    }

    const queryParts = query.split(/[\/:_-]+/).filter(Boolean);
    const candidateParts = candidate.split(/[\/:_-]+/).filter(Boolean);
    const overlap = queryParts.filter((part) => candidateParts.includes(part)).length;
    if (overlap > 0) {
        return 40 + overlap;
    }

    return 0;
}

function registerAutomaticSnapshotRefresh(context, outputChannel) {
    let timer = undefined;

    const scheduleRefresh = (reason) => {
        if (timer) {
            clearTimeout(timer);
        }

        timer = setTimeout(() => {
            timer = undefined;
            void refreshSnapshotsForWorkspace(outputChannel, reason);
        }, AUTO_EXPORT_DEBOUNCE_MS);
    };

    context.subscriptions.push(
        new vscode.Disposable(() => {
            if (timer) {
                clearTimeout(timer);
            }
        }),
        vscode.extensions.onDidChange(() => scheduleRefresh("extensions.onDidChange")),
        vscode.workspace.onDidChangeWorkspaceFolders(() => scheduleRefresh("workspaceFolders.onDidChange"))
    );

    scheduleRefresh("onStartupFinished");
}

async function refreshSnapshotsForWorkspace(outputChannel, reason) {
    try {
        const workspaceFolders = vscode.workspace.workspaceFolders || [];
        if (workspaceFolders.length === 0) {
            return;
        }

        await waitForToolRegistryToStabilize();

        const snapshot = collectToolSnapshot(workspaceFolders);
        if (snapshot.toolCount === 0) {
            outputChannel.appendLine(`[${reason}] Skipped snapshot refresh because no language model tools are registered yet.`);
            return;
        }

        await Promise.all(
            workspaceFolders.map((workspaceFolder) => writeSnapshotFile(workspaceFolder, snapshot))
        );

        outputChannel.appendLine(
            `[${reason}] Refreshed ${workspaceFolders.length} workspace snapshot(s) with ${snapshot.toolCount} tools.`
        );
    } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`[${reason}] Error: ${message}`);
    }
}

async function waitForToolRegistryToStabilize() {
    await delay(AUTO_EXPORT_INITIAL_DELAY_MS);

    let previousCount = -1;

    for (let attempt = 0; attempt < AUTO_EXPORT_STABILIZATION_ATTEMPTS; attempt += 1) {
        const currentCount = getLanguageModelTools().length;
        if (currentCount > 0 && currentCount === previousCount) {
            return;
        }

        previousCount = currentCount;
        await delay(AUTO_EXPORT_STABILIZATION_DELAY_MS);
    }
}

function delay(timeoutMs) {
    return new Promise((resolve) => setTimeout(resolve, timeoutMs));
}

async function writeSnapshotFile(workspaceFolder, snapshot) {
    const vscodeDir = vscode.Uri.joinPath(workspaceFolder.uri, ".vscode");
    const snapshotUri = vscode.Uri.joinPath(vscodeDir, SNAPSHOT_FILE_NAME);

    await vscode.workspace.fs.createDirectory(vscodeDir);
    await vscode.workspace.fs.writeFile(
        snapshotUri,
        Buffer.from(JSON.stringify(snapshot, null, 2) + "\n", "utf8")
    );

    return snapshotUri;
}

async function pickWorkspaceFolder() {
    const folders = vscode.workspace.workspaceFolders || [];
    if (folders.length === 0) {
        await vscode.window.showErrorMessage("Open a workspace folder before exporting a Copilot tool snapshot.");
        return null;
    }

    if (folders.length === 1) {
        return folders[0];
    }

    return vscode.window.showWorkspaceFolderPick({
        placeHolder: "Choose the workspace folder that should receive .vscode/copilot-tools.snapshot.json",
    });
}

function writeSnapshotSummary(outputChannel, snapshot, snapshotUri) {
    outputChannel.clear();
    outputChannel.appendLine(`Snapshot written to: ${snapshotUri.fsPath}`);
    outputChannel.appendLine(`Generated at: ${snapshot.generatedAt}`);
    outputChannel.appendLine(`Tool count: ${snapshot.toolCount}`);
    outputChannel.appendLine("");
    outputChannel.appendLine("Tool sets:");

    if (snapshot.toolSets.length === 0) {
        outputChannel.appendLine("- No grouped tool sets were derived from tool names or tags.");
    } else {
        for (const toolSet of snapshot.toolSets) {
            outputChannel.appendLine(`- ${toolSet.name}: ${toolSet.members.join(", ")}`);
        }
    }
}

module.exports = {
    activate,
    deactivate,
};