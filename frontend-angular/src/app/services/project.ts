import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { Project, StartProjectRequest, ChatMessage } from '../models/project';

const USE_MOCK = true; // toggle to false to use real backend

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private readonly apiUrl = 'http://127.0.0.1:8000';

  constructor(private readonly http: HttpClient) { }

  healthCheck(): Observable<{ status: string }> {
    if (USE_MOCK) return of({ status: 'ok' }).pipe(delay(120));
    return this.http.get<{ status: string }>(`${this.apiUrl}/health`);
  }

  createProject(request: StartProjectRequest): Observable<{ project_id: string }> {
    if (USE_MOCK) {
      const id = 'mock-' + Math.random().toString(36).slice(2,9);
      // seed a mock project into in-memory store
      MockStore.projects[id] = {
        id,
        description: request.description,
        appType: request.appType,
        useDb: request.useDb,
        useApis: request.useApis,
        userAuth: request.userAuth,
        intensiveTesting: request.intensiveTesting,
        workerCount: request.workerCount,
        isComplete: false,
        currentStage: 'planning',
        taskPlan: [
          { name: 'Manager planning', agent: 'manager', status: 'pending' },
          { name: 'Retriever gather data', agent: 'retriever', status: 'pending' },
          { name: 'Worker implement', agent: 'worker', status: 'pending' },
          { name: 'Tester verify', agent: 'tester', status: 'pending' }
        ],
        chatHistory: [],
        uploadedFiles: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      } as any;
      // start simulation automatically for newly created mock projects
      startMockSimulation(id);
      return of({ project_id: id }).pipe(delay(300));
    }
    return this.http.post<{ project_id: string }>(`${this.apiUrl}/projects`, request);
  }

  getProject(projectId: string): Observable<Project> {
    if (USE_MOCK) {
      const p = MockStore.projects[projectId];
      if (!p) {
        // return an observable that errors like a 404
        return of(null as unknown as Project).pipe(delay(80));
      }
      return of(p as Project).pipe(delay(120));
    }
    return this.http.get<Project>(`${this.apiUrl}/projects/${projectId}`);
  }

  sendChatMessage(projectId: string, message: ChatMessage): Observable<{ ok: boolean }> {
    if (USE_MOCK) {
      const p = MockStore.projects[projectId];
      if (p) {
        p.chatHistory.push(message);
        return of({ ok: true }).pipe(delay(80));
      }
      return of({ ok: false }).pipe(delay(80));
    }
    return this.http.post<{ ok: boolean }>(`${this.apiUrl}/projects/${projectId}/chat`, message);
  }

  uploadFiles(projectId: string, files: FileList): Observable<{ saved: string[] }> {
    if (USE_MOCK) {
      const p = MockStore.projects[projectId];
      const saved: string[] = [];
      if (p) {
        Array.from(files).forEach((f, i) => {
          const name = `mockfile-${Date.now()}-${i}-${f.name}`;
          p.uploadedFiles.push(name);
          saved.push(name);
        });
        return of({ saved }).pipe(delay(160));
      }
      return of({ saved: [] }).pipe(delay(80));
    }
    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    return this.http.post<{ saved: string[] }>(`${this.apiUrl}/projects/${projectId}/upload`, formData);
  }

  getPreview(projectId: string): Observable<{
    appType: string;
    description: string;
    status: string;
    isComplete: boolean;
  }> {
    if (USE_MOCK) {
      const p = MockStore.projects[projectId];
      if (!p) return of({ appType: 'web-app', description: 'Not found', status: 'unknown', isComplete: false }).pipe(delay(80));
      return of({ appType: p.appType, description: p.description, status: p.currentStage, isComplete: p.isComplete }).pipe(delay(80));
    }
    return this.http.get<{
      appType: string;
      description: string;
      status: string;
      isComplete: boolean;
    }>(`${this.apiUrl}/projects/${projectId}/preview`);
  }
}


// lightweight in-memory store for mocking during dev
const MockStore: { projects: Record<string, any> } = { projects: {} };

// Simulation timers for mock projects (only used when USE_MOCK = true)
const MockSimulations: Record<string, number[]> = {};

// Start a simulated run for a mock project (updates MockStore over time)
export function startMockSimulation(projectId: string) {
  if (!USE_MOCK) return;
  const p = MockStore.projects[projectId];
  if (!p) return;
  if (MockSimulations[projectId]) return; // already running

  MockSimulations[projectId] = [];

  const steps = [
    { stage: 'Manager planning', taskIndex: 0 },
    { stage: 'Retriever gather data', taskIndex: 1 },
    { stage: 'Worker implement', taskIndex: 2 },
    { stage: 'Tester verify', taskIndex: 3 },
    { stage: 'Build Complete', taskIndex: null }
  ];

  let delayAccum = 400; // initial delay

  steps.forEach((step, i) => {
    // start running the task
    const t1 = setTimeout(() => {
      if (step.taskIndex !== null) {
        p.taskPlan[step.taskIndex].status = 'running';
        p.currentStage = step.stage;
        p.updatedAt = new Date().toISOString();
      }
    }, delayAccum) as unknown as number;
    MockSimulations[projectId].push(t1);

    // after a bit, mark task completed and move on
    delayAccum += 900;
    const t2 = setTimeout(() => {
      if (step.taskIndex !== null) {
        p.taskPlan[step.taskIndex].status = 'completed';
        p.updatedAt = new Date().toISOString();
      } else {
        // final step: mark project complete
        p.isComplete = true;
        p.currentStage = 'Build Complete';
        p.updatedAt = new Date().toISOString();
      }
      // small update to ensure UI picks up change
    }, delayAccum) as unknown as number;
    MockSimulations[projectId].push(t2);

    // add spacing before next step
    delayAccum += 300;
  });
}

export function stopMockSimulation(projectId: string) {
  const timers = MockSimulations[projectId];
  if (!timers) return;
  timers.forEach(id => clearTimeout(id));
  delete MockSimulations[projectId];
}
