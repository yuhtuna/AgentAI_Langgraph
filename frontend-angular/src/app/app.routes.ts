import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/new-project', pathMatch: 'full' },
  { path: 'new-project', loadComponent: () => import('./components/new-project/new-project.component').then(m => m.NewProjectComponent) },
  { path: 'workflow/:id', loadComponent: () => import('./components/workflow/workflow.component').then(m => m.WorkflowComponent) },
  { path: 'workflow', loadComponent: () => import('./components/workflow/workflow.component').then(m => m.WorkflowComponent) },
  { path: 'chat/:id', loadComponent: () => import('./components/chat/chat.component').then(m => m.ChatComponent) },
  { path: 'chat', loadComponent: () => import('./components/chat/chat.component').then(m => m.ChatComponent) },
  { path: 'preview/:id', loadComponent: () => import('./components/preview/preview.component').then(m => m.PreviewComponent) },
  { path: 'preview', loadComponent: () => import('./components/preview/preview.component').then(m => m.PreviewComponent) },
  { path: 'code/:id', loadComponent: () => import('./components/code/code.component').then(m => m.CodeComponent) },
  { path: 'code', loadComponent: () => import('./components/code/code.component').then(m => m.CodeComponent) },
  { path: 'analytics/:id', loadComponent: () => import('./components/usage/usage.component').then(m => m.UsageComponent) },
  { path: 'analytics', loadComponent: () => import('./components/usage/usage.component').then(m => m.UsageComponent) },
  { path: 'usage/:id', loadComponent: () => import('./components/usage/usage.component').then(m => m.UsageComponent) },
  { path: 'usage', loadComponent: () => import('./components/usage/usage.component').then(m => m.UsageComponent) },
  { path: '**', redirectTo: '/new-project' } // Wildcard route for 404 - must be last
];
