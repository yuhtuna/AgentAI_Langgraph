import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProjectService } from '../../services/project';
import { Project } from '../../models/project';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectStateService } from '../../services/project-state.service';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-preview',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './preview.html',
  styleUrls: ['./preview.scss']
})
export class PreviewComponent implements OnInit, OnDestroy {
  project: Project | null = null;
  currentProjectId: string | null = null;
  pollingSubscription: Subscription | null = null;

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
  }

  startPolling() {
    if (!this.currentProjectId) return;

    this.pollingSubscription = interval(2000).subscribe(() => {
      this.projectService.getProject(this.currentProjectId!).subscribe({
        next: (project) => {
          this.project = project;
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

  getPreviewTitle(): string {
    if (!this.project) return 'Application Preview';
    
    switch (this.project.appType) {
      case 'web-app': return 'Web Application Preview';
      case 'api-service': return 'API Service Documentation';
      case 'ios-app': return 'iOS Application Preview';
      case 'android-app': return 'Android Application Preview';
      default: return 'Application Preview';
    }
  }

  // expose a public property for template binding / type-checking
  get previewTitle(): string {
    return this.getPreviewTitle();
  }

  getProjectTitle(): string {
    if (!this.project) return 'My App';
    
    // Extract app name from description or use default
    const description = this.project.description || 'My App';
    const words = description.split(' ').slice(0, 3).join(' ');
    return words.charAt(0).toUpperCase() + words.slice(1);
  }
}
