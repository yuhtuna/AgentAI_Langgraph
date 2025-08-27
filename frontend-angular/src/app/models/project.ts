export interface Project {
  id: string;
  description: string;
  appType: string;
  useDb: boolean;
  useApis: boolean;
  userAuth: boolean;
  intensiveTesting: boolean;
  workerCount: number;
  isComplete: boolean;
  currentStage: string;
  taskPlan: Task[];
  chatHistory: ChatMessage[];
  uploadedFiles: string[];
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  name: string;
  agent: string;
  status: 'pending' | 'running' | 'completed';
}

export interface ChatMessage {
  sender: string;
  text: string;
}

export interface StartProjectRequest {
  description: string;
  appType: string;
  useDb: boolean;
  useApis: boolean;
  userAuth: boolean;
  intensiveTesting: boolean;
  workerCount: number;
}
