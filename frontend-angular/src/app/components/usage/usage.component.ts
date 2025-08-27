import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { interval, Subscription } from 'rxjs';
import { ProjectService } from '../../services/project';
import { ProjectStateService } from '../../services/project-state.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Project } from '../../models/project';
import feather from 'feather-icons';

@Component({
  selector: 'app-usage',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './usage.component.html',
  styleUrls: ['./usage.component.scss']
})
export class UsageComponent implements OnInit, OnDestroy, AfterViewInit {
  project: Project | null = null;
  currentProjectId: string | null = null;
  pollingSubscription: Subscription | null = null;

  // simple cost metrics
  currentCost = 0.0;
  costEstimate = 0.0;

  // Mock user and analytics data
  totalUsers = 1245;
  newUsers = 32;
  pageAccessData = [
    { date: 'Aug 17', accesses: 120, newUsers: 10 },
    { date: 'Aug 18', accesses: 150, newUsers: 12 },
    { date: 'Aug 19', accesses: 180, newUsers: 8 },
    { date: 'Aug 20', accesses: 210, newUsers: 15 },
    { date: 'Aug 21', accesses: 190, newUsers: 9 },
    { date: 'Aug 22', accesses: 220, newUsers: 14 },
    { date: 'Aug 23', accesses: 250, newUsers: 16 }
  ];

  getAISummary(): string {
    return `User growth is steady (+32 new users this week). Page access is trending upward. Next steps: Focus on onboarding improvements, add more analytics, and optimize agent performance for higher retention.`;
  }

  constructor(
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly projectState: ProjectStateService
  ) {}

  ngOnInit() {
    this.currentProjectId = this.route.snapshot.paramMap.get('id') || this.projectState.getProjectId();
    if (!this.currentProjectId) {
      this.router.navigate(['/new-project']);
      return;
    }
    this.startPolling();
  }

  ngOnDestroy() {
    this.stopPolling();
  }

  startPolling() {
    if (!this.currentProjectId) return;
    this.pollingSubscription = interval(2000).subscribe(() => {
      this.projectService.getProject(this.currentProjectId!).subscribe({
        next: (project) => {
          this.project = project;
          this.recalculate();
          // Refresh feather icons if DOM changes
          setTimeout(() => feather.replace(), 0);
        },
        error: (error) => {
          console.error('Error polling project status:', error);
          this.stopPolling();
        }
      });
    });
  }

  stopPolling() {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
      this.pollingSubscription = null;
    }
  }

  recalculate() {
    if (!this.project) {
      this.currentCost = 0;
      this.costEstimate = 0;
      return;
    }

    const base = 0.2; // base runtime cost
    const perTask = 0.1; // per completed task
    const completed = this.project.taskPlan ? this.project.taskPlan.filter(t => t.status === 'completed').length : 0;
    this.currentCost = Number((base + completed * perTask).toFixed(2));

    // static monthly estimate for demo (matches basic_UI.html)
    this.costEstimate = 30.0;
  }

  getCostProgressWidth() {
    if (!this.project?.taskPlan) return '0%';
    const total = this.project.taskPlan.length || 1;
    const completed = this.project.taskPlan.filter(t => t.status === 'completed').length;
    return Math.round((completed / total) * 100) + '%';
  }

  ngAfterViewInit() {
    // Initialize feather icons
    feather.replace();
  }

  // Provide SVG points as component getters to avoid complex expressions in the template
  get pageAccessPoints(): string {
    return this.pageAccessData.map((d, i) => `${40 + i * 50},${100 - d.accesses / 3}`).join(' ');
  }

  get newUsersPoints(): string {
    return this.pageAccessData.map((d, i) => `${40 + i * 50},${100 - d.newUsers * 5}`).join(' ');
  }

  // Large chart versions for the prominent dashboard chart
  get pageAccessPointsLarge(): string {
    return this.pageAccessData.map((d, i) => `${80 + i * 90},${240 - d.accesses / 1.5}`).join(' ');
  }

  get newUsersPointsLarge(): string {
    return this.pageAccessData.map((d, i) => `${80 + i * 90},${240 - d.newUsers * 10}`).join(' ');
  }

  // Ensure shaded areas drop straight down by closing at the last x of the dataset
  get chartEndX(): number {
    return 80 + (this.pageAccessData.length - 1) * 90;
  }

  get accessAreaPolygonPoints(): string {
    return `80,240 ${this.pageAccessPointsLarge} ${this.chartEndX},240`;
  }

  get usersAreaPolygonPoints(): string {
    return `80,240 ${this.newUsersPointsLarge} ${this.chartEndX},240`;
  }

  // Analytics helper methods moved below for brevity
  getTotalTasks(): number { return this.project?.taskPlan?.length || 0; }
  getCompletedTasks(): number { return this.project?.taskPlan?.filter(t => t.status === 'completed').length || 0; }
  getInProgressTasks(): number { return this.project?.taskPlan?.filter(t => t.status === 'running').length || 0; }
  getFailedTasks(): number { return this.project?.taskPlan?.filter(t => t.status === 'pending').length || 0; }
  getCompletionPercentage(): number { const total = this.getTotalTasks(); return total > 0 ? Math.round((this.getCompletedTasks() / total) * 100) : 0; }
  getInProgressPercentage(): number { const total = this.getTotalTasks(); return total > 0 ? Math.round((this.getInProgressTasks() / total) * 100) : 0; }
  getFailedPercentage(): number { const total = this.getTotalTasks(); return total > 0 ? Math.round((this.getFailedTasks() / total) * 100) : 0; }
  getAverageTaskTime(): number { return 5; }
  getSuccessRate(): number { const total = this.getTotalTasks(); const completed = this.getCompletedTasks(); return total > 0 ? Math.round((completed / total) * 100) : 100; }
  getTimelineEvents() { return [ { type: 'success', title: 'Project Initialization', description: 'AI agents started project analysis', time: '2 hours ago' }, { type: 'progress', title: 'Database Schema Created', description: 'Generated database structure and models', time: '1.5 hours ago' }, { type: 'success', title: 'API Endpoints Generated', description: 'Created REST API with authentication', time: '1 hour ago' }, { type: 'progress', title: 'Frontend Development', description: 'Building user interface components', time: '30 minutes ago' } ]; }
}
