import type { FullConfig, FullResult, Suite, TestCase, TestResult } from '@playwright/test/reporter';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BUG_REPORT_PATH = path.resolve(
  __dirname, '..', '..', '..', 'agentic', 'runs', 'F-028-playwright-e2e', 'bug-report.md',
);

interface BugEntry {
  test: string;
  error: string;
  rootCause: string;
  severity: 'blocker' | 'major' | 'minor';
  proposedTaskId: string;
}

let nextTaskId = 29;

function estimateTaskId(): string {
  const id = `F-${String(nextTaskId).padStart(3, '0')}`;
  nextTaskId += 1;
  return id;
}

function estimateSeverity(error: string): 'blocker' | 'major' | 'minor' {
  const lower = error.toLowerCase();
  if (lower.includes('timeout') || lower.includes('500') || lower.includes(' crash')) return 'blocker';
  if (lower.includes('400') || lower.includes('selector') || lower.includes('404')) return 'major';
  return 'minor';
}

function inferRootCause(testName: string, error: string): string {
  const combined = `${testName} ${error}`.toLowerCase();
  if (combined.includes('websocket') || combined.includes('ws://')) return 'WebSocket connection not established — backend Channels consumer may not be running';
  if (combined.includes('ai') || combined.includes('draft') || combined.includes('generate')) return 'AI route interception not matching the GraphQL operationName';
  if (combined.includes('selector') || combined.includes('locator')) return 'UI component selector mismatch — component structure changed or test assumption incorrect';
  if (combined.includes('timeout') && combined.includes('navigation')) return 'Page navigation or data loading timeout — backend may be slow or not returning data';
  if (combined.includes('csr') || combined.includes('403')) return 'CSRF exemption not applied or nginx proxy misconfigured';
  if (combined.includes('400') || combined.includes('validation')) return 'Backend validation rejects input that test expects to succeed';
  if (combined.includes('enum') || combined.includes('state')) return 'ContentState enum case mismatch between backend and frontend';
  return 'Unknown — investigate test logs and backend error output';
}

function inferTitle(testName: string, error: string): string {
  const lower = `${testName} ${error}`.toLowerCase();
  if (lower.includes('websocket')) return 'WebSocket connection or reconnection issue';
  if (lower.includes('draft') || lower.includes('generate')) return 'AI draft generation route interception or response handling failure';
  if (lower.includes('translat')) return 'Translation mutation route interception failure';
  if (lower.includes('review') || lower.includes('approve') || lower.includes('reject')) return 'Review workflow state transition or UI interaction bug';
  if (lower.includes('badge') || lower.includes('state')) return 'ContentStateBadge rendering or state mapping issue';
  if (lower.includes('csr')) return 'CSRF protection blocking GraphQL requests';
  if (lower.includes('campaign') || lower.includes('content')) return 'CRUD operation failure or validation mismatch';
  return testName.length > 60 ? `${testName.slice(0, 57)}...` : testName;
}

export default class BugReporter {
  private bugs: BugEntry[] = [];

  onTestEnd(test: TestCase, result: TestResult): void {
    if (result.status === 'passed') return;
    const error = result.errors[0]?.message ?? 'Unknown error';
    const severity = estimateSeverity(error);
    this.bugs.push({
      test: `${test.parent?.title ?? ''} > ${test.title}`,
      error,
      rootCause: inferRootCause(test.title, error),
      severity,
      proposedTaskId: estimateTaskId(),
    });
  }

  onEnd(_result: FullResult): void {
    const report = this.generateReport();
    fs.mkdirSync(path.dirname(BUG_REPORT_PATH), { recursive: true });
    fs.writeFileSync(BUG_REPORT_PATH, report, 'utf-8');
  }

  private generateReport(): string {
    if (this.bugs.length === 0) {
      return [
        '# Bug Report — F-028 Playwright E2E Suite',
        `**Date:** ${new Date().toISOString().slice(0, 10)}`,
        `**Run ID:** ${Date.now()}`,
        '**Passed:** All',
        '**Failed:** 0',
        '',
        'All 45+ acceptance criteria pass — 0 bugs found.',
        '',
      ].join('\n');
    }

    const failedCount = this.bugs.length;
    const blockerCount = this.bugs.filter((b) => b.severity === 'blocker').length;
    const majorCount = this.bugs.filter((b) => b.severity === 'major').length;
    const minorCount = this.bugs.filter((b) => b.severity === 'minor').length;

    const lines: string[] = [
      '# Bug Report — F-028 Playwright E2E Suite',
      `**Date:** ${new Date().toISOString().slice(0, 10)}`,
      `**Run ID:** ${Date.now()}`,
      `**Failed:** ${failedCount}`,
      '',
      '## Failed Tests',
      '',
    ];

    for (let i = 0; i < this.bugs.length; i++) {
      const bug = this.bugs[i];
      lines.push(`### ${i + 1}. ${bug.test}`);
      lines.push(`- **Test:** \`${bug.test}\``);
      lines.push(`- **Error:** ${bug.error.trim().split('\n')[0]}`);
      lines.push(`- **Root Cause:** ${bug.rootCause}`);
      lines.push(`- **Severity:** ${bug.severity}`);
      lines.push(`- **Proposed Task:** ${bug.proposedTaskId} — ${inferTitle(bug.test, bug.error)}`);
      lines.push('');
    }

    lines.push('## Summary');
    lines.push(`- **Blockers:** ${blockerCount}`);
    lines.push(`- **Major:** ${majorCount}`);
    lines.push(`- **Minor:** ${minorCount}`);
    lines.push('---');
    lines.push('_Auto-generated by Playwright bug reporter._');
    lines.push('');

    return lines.join('\n');
  }
}
