# install.ps1 — install skills from this repo into popular AI coding tools
#
# Usage:
#   .\install.ps1                          # interactive: pick skills and agents
#   .\install.ps1 --all                    # all skills, auto-detected agents
#   .\install.ps1 --all -a cursor -a claude-code -g
#   .\install.ps1 -s docker -a opencode --copy
#   .\install.ps1 -s docker -a cursor --as-rule
#   .\install.ps1 --all -a claude-code -a windsurf --as-rule -g -y
#   .\install.ps1 --list
#   .\install.ps1 --list-agents
#
# Run from a clone of this repo, or:
#   irm https://raw.githubusercontent.com/brianlechthaler/skills/main/install.ps1 -OutFile install.ps1
#   .\install.ps1 --all -y

#Requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Script:RepoRoot = if ($env:SKILLS_REPO_ROOT) { $env:SKILLS_REPO_ROOT } else { $PSScriptRoot }
$Script:TmpRepo = $null
$Script:Global = $false
$Script:Method = 'symlink'
$Script:Yes = $false
$Script:AsRule = $false
$Script:Skills = @()
$Script:Agents = @()
$Script:InstallAllSkills = $false

$Script:AgentDefs = @(
    @{ Id = 'cursor'; Project = '.cursor/skills'; Global = '~/.cursor/skills' }
    @{ Id = 'claude-code'; Project = '.claude/skills'; Global = '~/.claude/skills' }
    @{ Id = 'opencode'; Project = '.opencode/skills'; Global = '~/.config/opencode/skills' }
    @{ Id = 'codex'; Project = '.codex/skills'; Global = '~/.codex/skills' }
    @{ Id = 'windsurf'; Project = '.windsurf/skills'; Global = '~/.codeium/windsurf/skills' }
    @{ Id = 'github-copilot'; Project = '.github/skills'; Global = '~/.copilot/skills' }
    @{ Id = 'gemini-cli'; Project = '.gemini/skills'; Global = '~/.gemini/skills' }
    @{ Id = 'cline'; Project = '.agents/skills'; Global = '~/.agents/skills' }
    @{ Id = 'roo'; Project = '.roo/skills'; Global = '~/.roo/skills' }
    @{ Id = 'continue'; Project = '.continue/skills'; Global = '~/.continue/skills' }
    @{ Id = 'trae'; Project = '.trae/skills'; Global = '~/.trae/skills' }
    @{ Id = 'universal'; Project = '.agents/skills'; Global = '~/.agents/skills' }
)

$Script:RuleDefs = @(
    @{ Id = 'cursor'; Project = '.cursor/rules'; Global = '~/.cursor/rules'; Format = 'cursor'; Delivery = 'per-file' }
    @{ Id = 'claude-code'; Project = '.claude/rules'; Global = '~/.claude/rules'; Format = 'claude'; Delivery = 'per-file' }
    @{ Id = 'windsurf'; Project = '.windsurf/rules'; Global = '~/.codeium/windsurf/memories/global_rules.md'; Format = 'windsurf'; Delivery = 'per-file' }
    @{ Id = 'github-copilot'; Project = '.github/copilot-instructions.md'; Global = '~/.copilot/copilot-instructions.md'; Format = 'plain'; Delivery = 'append' }
    @{ Id = 'opencode'; Project = 'AGENTS.md'; Global = '~/.opencode/AGENTS.md'; Format = 'plain'; Delivery = 'append' }
    @{ Id = 'codex'; Project = 'AGENTS.md'; Global = '~/.codex/AGENTS.md'; Format = 'plain'; Delivery = 'append' }
    @{ Id = 'gemini-cli'; Project = 'GEMINI.md'; Global = '~/.gemini/GEMINI.md'; Format = 'plain'; Delivery = 'append' }
    @{ Id = 'cline'; Project = '.agents/rules'; Global = '~/.agents/rules'; Format = 'plain'; Delivery = 'per-file' }
    @{ Id = 'roo'; Project = '.roo/rules'; Global = '~/.roo/rules'; Format = 'plain'; Delivery = 'per-file' }
    @{ Id = 'continue'; Project = '.continue/rules'; Global = '~/.continue/rules'; Format = 'plain'; Delivery = 'per-file' }
    @{ Id = 'trae'; Project = '.trae/rules'; Global = '~/.trae/rules'; Format = 'plain'; Delivery = 'per-file' }
    @{ Id = 'universal'; Project = '.agents/rules'; Global = '~/.agents/rules'; Format = 'plain'; Delivery = 'per-file' }
)

function Write-Err {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Message)
    Write-Error ("error: " + ($Message -join ' '))
    exit 1
}

function Write-Info {
    param([string]$Message)
    Write-Host "→ $Message"
}

function Write-Ok {
    param([string]$Message)
    Write-Host "✓ $Message"
}

function Expand-HomePath {
    param([string]$Path)
    if ($Path.StartsWith('~/')) {
        return Join-Path $HOME $Path.Substring(2)
    }
    return $Path
}

function Show-Usage {
    @'
Install skills from this repository into AI coding tool skill directories.

Usage:
  install.ps1 [options] [skill...]

Options:
  -h, --help           Show this help
  --list               List skills available in this repo
  --list-agents        List supported agents and install paths
  -s, --skill NAME     Install specific skill(s); repeatable
  --all                Install all skills in this repo
  -a, --agent NAME     Target agent(s); repeatable (see --list-agents)
  -g, --global         Install to user home dirs instead of current project
  --copy               Copy files instead of symlinking (default: symlink)
  --as-rule            Install as AI rules instead of skills (see --list-agents)
  -y, --yes            Skip confirmation prompts

Examples:
  .\install.ps1 --list
  .\install.ps1 --all -a cursor -a claude-code
  .\install.ps1 -s docker -g -a opencode -a codex -y
  .\install.ps1 -s test -a cursor --as-rule
  .\install.ps1 --all -a windsurf -a claude-code --as-rule -g -y
  .\install.ps1 --all --copy -g -y

Popular agents: cursor, claude-code, opencode, codex, windsurf, github-copilot,
gemini-cli, cline, roo, universal

Use --agent all to install to all supported agents.
'@ | Write-Host
}

function Get-AgentProjectPath {
    param([string]$Id)
    $def = $Script:AgentDefs | Where-Object { $_.Id -eq $Id } | Select-Object -First 1
    if (-not $def) { return $null }
    return $def.Project
}

function Get-AgentGlobalPath {
    param([string]$Id)
    $def = $Script:AgentDefs | Where-Object { $_.Id -eq $Id } | Select-Object -First 1
    if (-not $def) { return $null }
    return $def.Global
}

function Test-AgentExists {
    param([string]$Id)
    return [bool](Get-AgentProjectPath -Id $Id)
}

function Test-RuleExists {
    param([string]$Id)
    return [bool]($Script:RuleDefs | Where-Object { $_.Id -eq $Id } | Select-Object -First 1)
}

function Get-RuleDefForAgent {
    param([string]$Id)
    return $Script:RuleDefs | Where-Object { $_.Id -eq $Id } | Select-Object -First 1
}

function Resolve-RuleTarget {
    param([string]$Id)

    $def = Get-RuleDefForAgent -Id $Id
    if (-not $def) { Write-Err "no rule mapping for agent: $Id" }

    if ($Script:Global) {
        if ($Id -eq 'windsurf') {
            return @{
                Target = Join-Path $HOME '.codeium/windsurf/memories/global_rules.md'
                Delivery = 'append'
                Format = 'windsurf'
            }
        }
        $rel = Expand-HomePath $def.Global
        return @{
            Target = $rel
            Delivery = $def.Delivery
            Format = $def.Format
        }
    }

    if ($Id -eq 'windsurf') {
        return @{
            Target = Join-Path (Get-Location) '.windsurf/rules'
            Delivery = 'per-file'
            Format = 'windsurf'
        }
    }

    if ($def.Delivery -eq 'append') {
        return @{
            Target = Join-Path (Get-Location) $def.Project
            Delivery = 'append'
            Format = $def.Format
        }
    }

    return @{
        Target = Join-Path (Get-Location) $def.Project
        Delivery = 'per-file'
        Format = $def.Format
    }
}

function Get-RuleFilenameForSkill {
    param([string]$Skill, [string]$Format)
    if ($Format -eq 'cursor') { return "$Skill.mdc" }
    return "$Skill.md"
}

function Convert-SkillToRule {
    param([string]$SkillFile, [string]$Format)

    $text = Get-Content -Raw -LiteralPath $SkillFile
    $meta = @{}
    $body = $text

    if ($text -match '(?s)^---\r?\n(.*?)\r?\n---\r?\n(.*)$') {
        $frontmatter = $Matches[1]
        $body = $Matches[2]

        if ($frontmatter -match '(?m)^name:\s*(.+)$') {
            $meta['name'] = $Matches[1].Trim().Trim('"', "'")
        }

        if ($frontmatter -match '(?ms)^description:\s*>?-?\s*\r?\n((?:[ \t]+.+\r?\n?)+)') {
            $desc = $Matches[1] -replace '(?m)\r?\n[ \t]+', ' '
            $meta['description'] = $desc.Trim()
        }
        elseif ($frontmatter -match '(?m)^description:\s*(.+)$') {
            $meta['description'] = $Matches[1].Trim().Trim('"', "'")
        }
    }

    $skillDir = Split-Path -Parent $SkillFile
    $name = if ($meta['name']) { $meta['name'] } else { Split-Path -Leaf $skillDir }
    $description = if ($meta['description']) { $meta['description'] } else { $name }

    switch ($Format) {
        'cursor' {
            return (@"
---
description: $description
alwaysApply: false
---
$body
"@)
        }
        'claude' {
            return (@"
---
---
$body
"@)
        }
        'windsurf' {
            return (@"
---
trigger: model_decision
description: $description
---
$body
"@)
        }
        default {
            $title = (Get-Culture).TextInfo.ToTitleCase($name.Replace('-', ' '))
            $lines = @("# $title", '')
            if ($description -and $description -ne $name) {
                $lines += "> $description"
                $lines += ''
            }
            $lines += $body
            return ($lines -join "`n")
        }
    }
}

function Update-MarkedSection {
    param([string]$Target, [string]$Skill, [string]$Content)

    $begin = "<!-- skills-install:${Skill}:begin -->"
    $end = "<!-- skills-install:${Skill}:end -->"
    $dir = Split-Path -Parent $Target

    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    if (-not (Test-Path -LiteralPath $Target)) {
        New-Item -ItemType File -Path $Target -Force | Out-Null
    }

    $existing = Get-Content -Raw -LiteralPath $Target
    if ($existing -match [regex]::Escape($begin)) {
        $pattern = "(?s)$([regex]::Escape($begin)).*?$([regex]::Escape($end))\r?\n?"
        $existing = [regex]::Replace($existing, $pattern, '')
    }

    $section = "`n$begin`n$content`n$end`n"
    if ($existing -and -not $existing.EndsWith("`n")) {
        $existing += "`n"
    }
    Set-Content -LiteralPath $Target -Value ($existing + $section) -NoNewline
}

function Get-AllAgentIds {
    return $Script:AgentDefs | ForEach-Object { $_.Id }
}

function Resolve-AgentDir {
    param([string]$Id)

    if ($Script:Global) {
        $rel = Get-AgentGlobalPath -Id $Id
        if (-not $rel) { Write-Err "unknown agent: $Id" }
        return Expand-HomePath $rel
    }

    $rel = Get-AgentProjectPath -Id $Id
    if (-not $rel) { Write-Err "unknown agent: $Id" }
    return Join-Path (Get-Location) $rel
}

function Get-DiscoveredSkills {
    param([string]$Root)

    if (-not (Test-Path -LiteralPath $Root)) {
        return @()
    }

    $found = [System.Collections.Generic.List[string]]::new()
    foreach ($dir in Get-ChildItem -LiteralPath $Root -Directory) {
        $name = $dir.Name
        if ($name.StartsWith('.')) { continue }
        $skillFile = Join-Path $dir.FullName 'SKILL.md'
        if (Test-Path -LiteralPath $skillFile) {
            [void]$found.Add($name)
        }
    }
    return $found.ToArray()
}

function Get-SkillList {
    $found = @(Get-DiscoveredSkills -Root $Script:RepoRoot)
    if ($found.Count -eq 0) {
        Write-Err "no skills found in $($Script:RepoRoot) (expected <skill>/SKILL.md directories)"
    }
    return $found
}

function Show-AgentList {
    Write-Host ("{0,-18} {1,-28} {2}" -f 'AGENT', 'SKILL PROJECT', 'SKILL GLOBAL')
    foreach ($def in $Script:AgentDefs) {
        Write-Host ("{0,-18} {1,-28} {2}" -f $def.Id, $def.Project, $def.Global)
    }
    Write-Host ''
    Write-Host ("{0,-18} {1,-36} {2}" -f 'AGENT', 'RULE PROJECT', 'RULE GLOBAL')
    foreach ($def in $Script:RuleDefs) {
        Write-Host ("{0,-18} {1,-36} {2}" -f $def.Id, $def.Project, $def.Global)
    }
    Write-Host ''
    Write-Host 'Use --as-rule to install skills as rules instead of skill directories.'
    Write-Host 'Windsurf global rules append to ~/.codeium/windsurf/memories/global_rules.md'
}

function Get-DetectedAgents {
    $detected = [System.Collections.Generic.List[string]]::new()

    if ((Test-Path (Join-Path $HOME '.cursor')) -or (Get-Command cursor -ErrorAction SilentlyContinue)) {
        [void]$detected.Add('cursor')
    }
    if ((Test-Path (Join-Path $HOME '.claude')) -or (Get-Command claude -ErrorAction SilentlyContinue)) {
        [void]$detected.Add('claude-code')
    }
    if ((Test-Path (Join-Path $HOME '.config/opencode')) -or (Get-Command opencode -ErrorAction SilentlyContinue)) {
        [void]$detected.Add('opencode')
    }
    if ((Test-Path (Join-Path $HOME '.codex')) -or (Get-Command codex -ErrorAction SilentlyContinue)) {
        [void]$detected.Add('codex')
    }
    if ((Test-Path (Join-Path $HOME '.codeium/windsurf')) -or (Get-Command windsurf -ErrorAction SilentlyContinue)) {
        [void]$detected.Add('windsurf')
    }
    if (Test-Path (Join-Path $HOME '.copilot')) {
        [void]$detected.Add('github-copilot')
    }
    if ((Test-Path (Join-Path $HOME '.gemini')) -or (Get-Command gemini -ErrorAction SilentlyContinue)) {
        [void]$detected.Add('gemini-cli')
    }

    if ($detected.Count -eq 0) {
        return @('cursor', 'claude-code', 'opencode')
    }
    return $detected.ToArray()
}

function Expand-Agents {
    param([string[]]$InputAgents)

    $expanded = [System.Collections.Generic.List[string]]::new()
    foreach ($a in $InputAgents) {
        if ($a -eq 'all') {
            foreach ($id in Get-AllAgentIds) { [void]$expanded.Add($id) }
        }
        else {
            if ($Script:AsRule) {
                if (-not (Test-RuleExists -Id $a)) {
                    Write-Err "unknown agent for --as-rule: $a (see --list-agents)"
                }
            }
            elseif (-not (Test-AgentExists -Id $a)) {
                Write-Err "unknown agent: $a (see --list-agents)"
            }
            [void]$expanded.Add($a)
        }
    }
    $Script:Agents = $expanded.ToArray()
}

function Expand-Skills {
    $available = @(Get-SkillList)
    if ($Script:InstallAllSkills) {
        $Script:Skills = $available
        return
    }
    if ($Script:Skills.Count -eq 0) {
        $Script:Skills = $available
        return
    }
    foreach ($want in $Script:Skills) {
        if ($available -notcontains $want) {
            Write-Err "unknown skill: $want (see --list)"
        }
    }
}

function Install-SkillForAgent {
    param([string]$Skill, [string]$Agent)

    $src = Join-Path $Script:RepoRoot $Skill
    $skillFile = Join-Path $src 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillFile)) {
        Write-Err "missing skill source: $src"
    }

    $agentDir = Resolve-AgentDir -Id $Agent
    $dest = Join-Path $agentDir $Skill

    if (-not (Test-Path -LiteralPath $agentDir)) {
        New-Item -ItemType Directory -Path $agentDir -Force | Out-Null
    }

    if (Test-Path -LiteralPath $dest) {
        $item = Get-Item -LiteralPath $dest -Force
        if ($item.LinkType -eq 'SymbolicLink') {
            Remove-Item -LiteralPath $dest -Force
        }
        elseif ($item.PSIsContainer) {
            Write-Info "$Agent`: replacing existing $dest"
            Remove-Item -LiteralPath $dest -Recurse -Force
        }
        else {
            Remove-Item -LiteralPath $dest -Force
        }
    }

    if ($Script:Method -eq 'copy') {
        Copy-Item -LiteralPath $src -Destination $dest -Recurse -Force
    }
    else {
        try {
            New-Item -ItemType SymbolicLink -Path $dest -Target $src -Force | Out-Null
        }
        catch {
            Write-Info "symlink failed, using copy: $($_.Exception.Message)"
            Copy-Item -LiteralPath $src -Destination $dest -Recurse -Force
        }
    }

    if (-not $IsWindows -and (Get-Command chmod -ErrorAction SilentlyContinue)) {
        Get-ChildItem -LiteralPath $dest -Filter '*.sh' -Recurse -File -ErrorAction SilentlyContinue |
            ForEach-Object { & chmod +x $_.FullName }
    }

    Write-Ok "$Skill -> $dest ($Agent)"
}

function Install-SkillAsRuleForAgent {
    param([string]$Skill, [string]$Agent)

    $src = Join-Path $Script:RepoRoot "$Skill/SKILL.md"
    if (-not (Test-Path -LiteralPath $src)) {
        Write-Err "missing skill source: $src"
    }

    $targetInfo = Resolve-RuleTarget -Id $Agent
    $content = Convert-SkillToRule -SkillFile $src -Format $targetInfo.Format

    if ($targetInfo.Delivery -eq 'append') {
        Update-MarkedSection -Target $targetInfo.Target -Skill $Skill -Content $content
        Write-Ok "$Skill -> $($targetInfo.Target) ($Agent rule)"
        return
    }

    $filename = Get-RuleFilenameForSkill -Skill $Skill -Format $targetInfo.Format
    $targetFile = Join-Path $targetInfo.Target $filename
    $targetDir = Split-Path -Parent $targetFile
    if (-not (Test-Path -LiteralPath $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    Set-Content -LiteralPath $targetFile -Value $content
    Write-Ok "$Skill -> $targetFile ($Agent rule)"
}

function Test-Confirm {
    param([string]$Prompt)
    if ($Script:Yes) { return $true }
    $reply = Read-Host "$Prompt [y/N]"
    return $reply -match '^[Yy]$'
}

function Invoke-Cleanup {
    if ($Script:TmpRepo -and (Test-Path -LiteralPath $Script:TmpRepo)) {
        Remove-Item -LiteralPath $Script:TmpRepo -Recurse -Force
        $Script:TmpRepo = $null
    }
}

function Invoke-FetchRepoIfNeeded {
    $skills = @(Get-DiscoveredSkills -Root $Script:RepoRoot)
    if ($skills.Count -gt 0) { return }

    $repo = if ($env:SKILLS_GITHUB_REPO) { $env:SKILLS_GITHUB_REPO } else { 'brianlechthaler/skills' }
    $branch = if ($env:SKILLS_GITHUB_BRANCH) { $env:SKILLS_GITHUB_BRANCH } else { 'main' }
    $tarball = "https://github.com/$repo/archive/refs/heads/$branch.tar.gz"

    Write-Info "fetching skills from github.com/$repo ($branch)..."
    $Script:TmpRepo = Join-Path ([System.IO.Path]::GetTempPath()) ("skills-install-" + [guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $Script:TmpRepo -Force | Out-Null

    $archive = Join-Path $Script:TmpRepo 'archive.tar.gz'
    Invoke-WebRequest -Uri $tarball -OutFile $archive -UseBasicParsing

    if (Get-Command tar -ErrorAction SilentlyContinue) {
        & tar -xzf $archive -C $Script:TmpRepo --strip-components=1
    }
    else {
        Write-Err 'tar is required to extract the remote skills archive'
    }

    Remove-Item -LiteralPath $archive -Force
    $Script:RepoRoot = $Script:TmpRepo

    if ($Script:Method -eq 'symlink') {
        Write-Info 'using copy mode for remote install (symlinks would not persist)'
        $Script:Method = 'copy'
    }
}

try {
    $Action = 'install'
    $argsList = @($args)

    $i = 0
    while ($i -lt $argsList.Count) {
        $arg = $argsList[$i]
        switch ($arg) {
            { $_ -in '-h', '--help' } { Show-Usage; exit 0 }
            '--list' { $Action = 'list'; $i++; continue }
            '--list-agents' { $Action = 'list-agents'; $i++; continue }
            '--all' { $Script:InstallAllSkills = $true; $i++; continue }
            { $_ -in '-g', '--global' } { $Script:Global = $true; $i++; continue }
            '--copy' { $Script:Method = 'copy'; $i++; continue }
            '--as-rule' { $Script:AsRule = $true; $Script:Method = 'copy'; $i++; continue }
            { $_ -in '-y', '--yes' } { $Script:Yes = $true; $i++; continue }
            { $_ -in '-s', '--skill' } {
                $i++
                if ($i -ge $argsList.Count) { Write-Err "missing value for $arg" }
                $Script:Skills += $argsList[$i]
                $i++
                continue
            }
            { $_ -in '-a', '--agent' } {
                $i++
                if ($i -ge $argsList.Count) { Write-Err "missing value for $arg" }
                $Script:Agents += $argsList[$i]
                $i++
                continue
            }
            { $_.StartsWith('-') } { Write-Err "unknown option: $arg" }
            default {
                $Script:Skills += $arg
                $i++
                continue
            }
        }
    }

    if (-not (Test-Path -LiteralPath $Script:RepoRoot)) {
        Write-Err "repo root not found: $($Script:RepoRoot)"
    }

    if ($Action -eq 'list-agents') {
        Show-AgentList
        exit 0
    }

    if ($Action -eq 'list') {
        Invoke-FetchRepoIfNeeded
        Get-SkillList | ForEach-Object { Write-Output $_ }
        exit 0
    }

    Invoke-FetchRepoIfNeeded
    Expand-Skills

    if ($Script:Agents.Count -eq 0) {
        $detected = Get-DetectedAgents
        $Script:Agents = $detected
        Write-Info "auto-detected agents: $($detected -join ' ')"
    }

    Expand-Agents -InputAgents $Script:Agents

    $scope = if ($Script:Global) { "global ($HOME)" } else { "project ($(Get-Location))" }
    $installMode = if ($Script:AsRule) { 'rules' } else { 'skills' }

    Write-Host ''
    Write-Host "Skills : $($Script:Skills -join ' ')"
    Write-Host "Agents : $($Script:Agents -join ' ')"
    Write-Host "Scope  : $scope"
    Write-Host "Mode   : $installMode"
    if (-not $Script:AsRule) {
        Write-Host "Method : $($Script:Method)"
    }
    Write-Host ''

    if (-not (Test-Confirm -Prompt 'Proceed with installation?')) {
        Write-Host 'cancelled.'
        exit 0
    }

    foreach ($agent in $Script:Agents) {
        foreach ($skill in $Script:Skills) {
            if ($Script:AsRule) {
                Install-SkillAsRuleForAgent -Skill $skill -Agent $agent
            }
            else {
                Install-SkillForAgent -Skill $skill -Agent $agent
            }
        }
    }

    Write-Host ''
    if ($Script:AsRule) {
        Write-Ok "installed $($Script:Skills.Count) rule(s) to $($Script:Agents.Count) agent(s)."
    }
    else {
        Write-Ok "installed $($Script:Skills.Count) skill(s) to $($Script:Agents.Count) agent(s)."
    }
    Write-Host 'Restart your coding tool or start a new session to pick up changes.'
}
finally {
    Invoke-Cleanup
}
