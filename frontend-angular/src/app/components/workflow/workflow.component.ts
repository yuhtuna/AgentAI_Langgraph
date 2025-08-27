import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProjectService, startMockSimulation, stopMockSimulation } from '../../services/project';
import { Project } from '../../models/project';
import { interval, Subscription } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectStateService } from '../../services/project-state.service';

@Component({
  selector: 'app-workflow',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './workflow.component.html',
  styleUrl: './workflow.component.scss'
})
export class WorkflowComponent implements OnInit, OnDestroy {
  project: Project | null = null;
  currentProjectId: string | null = null;
  pollingSubscription: Subscription | null = null;
  simulationRunning = false;
  progress = 0; // percent 0-100 based on completed tasks
  // make getNodeStatus a public method so template bindings can call it reliably
  public getNodeStatus(agent: string): string {
    return this.getNodeStatusImpl(agent);
  }

  constructor(
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly projectState: ProjectStateService
  ) {}

  ngOnInit() {
    // Try route first, then fallback to service
    this.currentProjectId = this.route.snapshot.paramMap.get('id') || this.projectState.getProjectId();
    if (!this.currentProjectId) {
      // no project id available, redirect back to new-project
      this.router.navigate(['/new-project']);
      return;
    }
    this.startPolling();
  }

  ngOnDestroy() {
    this.stopPolling();
    this.stopSimulation();
  }

  startPolling() {
    if (!this.currentProjectId) return;

    this.pollingSubscription = interval(2000).subscribe(() => {
      this.projectService.getProject(this.currentProjectId!).subscribe({
        next: (project) => {
          this.project = project;
          this.updateProgress();
          // auto-start simulation for mock projects when project data first appears
          if (!this.simulationRunning && project && !project.isComplete) {
            this.startSimulation();
          }
          if (project.isComplete) {
            this.stopPolling();
            this.stopSimulation();
          }
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

  startSimulation() {
    if (!this.currentProjectId) return;
    startMockSimulation(this.currentProjectId);
    this.simulationRunning = true;
  }

  stopSimulation() {
    if (!this.currentProjectId) return;
    stopMockSimulation(this.currentProjectId);
    this.simulationRunning = false;
  }

  deploy() {
    // navigate to the preview/deploy page and ensure the preview component can pick up the project
    if (!this.currentProjectId) return;
    // save current project id in shared state (PreviewComponent reads from ProjectStateService as a fallback)
    this.projectState.setProjectId(this.currentProjectId);
    // navigate to the preview page
    this.router.navigate(['/preview']);
  }

  updateProgress() {
    if (!this.project || !this.project.taskPlan || this.project.taskPlan.length === 0) {
      this.progress = 0;
      return;
    }
    const total = this.project.taskPlan.length;
    const completed = this.project.taskPlan.filter(t => t.status === 'completed').length;
    this.progress = Math.round((completed / total) * 100);
  }

  // underlying implementation used by the instance function
  private getNodeStatusImpl(agent: string) {
    if (!this.project) return 'pending';
    const t = this.project.taskPlan.find(x => x.agent === agent || x.agent.toLowerCase() === agent.toLowerCase());
    return t ? t.status : 'pending';
  }

  getTaskIconClass(status: string) {
    switch (status) {
      case 'completed':
        return 'task-done';
      case 'running':
        return 'task-running';
      default:
        return 'task-pending';
    }
  }

  getTaskIcon(status: string) {
    switch (status) {
      case 'completed':
        return '✔️';
      case 'running':
        return '⏳';
      default:
        return '•';
    }
  }

  // Return lucide icon name for a given task status
  getTaskIconName(status: string) {
    switch (status) {
      case 'completed':
        return 'check-circle';
      case 'running':
        return 'clock';
      default:
        return 'circle';
    }
  }
}