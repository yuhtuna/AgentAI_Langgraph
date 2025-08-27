import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ProjectStateService {
  private _currentProjectId: string | null = null;

  setProjectId(id: string | null) {
    this._currentProjectId = id;
  }

  getProjectId(): string | null {
    return this._currentProjectId;
  }

  clear() {
    this._currentProjectId = null;
  }
}
