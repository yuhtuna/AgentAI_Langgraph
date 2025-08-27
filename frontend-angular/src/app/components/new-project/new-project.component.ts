import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProjectService } from '../../services/project';
import { StartProjectRequest } from '../../models/project';
import { Router } from '@angular/router';
import { RouterModule } from '@angular/router';
import { ProjectStateService } from '../../services/project-state.service';
import { createIcons, Rocket } from 'lucide';

@Component({
  selector: 'app-new-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  host: { 'ngSkipHydration': '' },
  templateUrl: './new-project.component.html',
  styleUrl: './new-project.component.scss'
})
export class NewProjectComponent implements AfterViewInit {
  projectRequest: StartProjectRequest = {
    description: '',
    appType: 'web-app',
    useDb: false,
    useApis: false,
    userAuth: false,
    intensiveTesting: false,
    workerCount: 3
  };

  uploadedFiles: File[] = [];

  constructor(
    private readonly projectService: ProjectService,
    private readonly router: Router,
    private readonly projectState: ProjectStateService
  ) {}

  ngAfterViewInit() {
    // Initialize Lucide icons after the view is initialized
    setTimeout(() => {
      try {
        // Pass the specific icons we need
        createIcons({
          icons: {
            rocket: Rocket
          }
        });
        
        // Double-check that the rocket icon loaded properly
        setTimeout(() => {
          const rocketIcon = document.querySelector('[data-lucide="rocket"]');
          if (rocketIcon && !rocketIcon.querySelector('svg')) {
            console.warn('Lucide rocket icon did not load, fallback will be used');
          }
        }, 100);
      } catch (error) {
        console.warn('Lucide icons failed to initialize:', error);
      }
    }, 0);
  }

  startProject() {
    if (!this.projectRequest.description.trim()) {
      alert('Please provide a description for your application.');
      return;
    }

    this.projectService.createProject(this.projectRequest).subscribe({
      next: (response) => {
        console.log('Project created:', response.project_id);
        this.projectState.setProjectId(response.project_id);
        // navigate with the project id as a route param
        this.router.navigate(['/workflow', response.project_id]);
      },
      error: (error) => {
        console.error('Error creating project:', error);
        alert('Failed to create project. Please try again.');
      }
    });
  }

  // accept nullable/undefined FileList from template events
  handleFiles(files: FileList | null | undefined) {
    if (!files) return;
    Array.from(files).forEach(file => {
      if (!this.uploadedFiles.some(f => f.name === file.name)) {
        this.uploadedFiles.push(file);
      }
    });
  }

  removeFile(file: File) {
    this.uploadedFiles = this.uploadedFiles.filter(f => f.name !== file.name);
  }
}