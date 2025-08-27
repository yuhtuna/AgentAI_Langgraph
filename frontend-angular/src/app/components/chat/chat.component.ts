import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProjectService } from '../../services/project';
import { ChatMessage } from '../../models/project';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectStateService } from '../../services/project-state.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  messages: ChatMessage[] = [];
  newMessage = '';
  currentProjectId: string | null = null;

  constructor(
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly projectState: ProjectStateService
  ) {}

  ngOnInit() {
    // Try route first then fallback to state service
    this.currentProjectId = this.route.snapshot.paramMap.get('id') || this.projectState.getProjectId();
    if (!this.currentProjectId) {
      this.router.navigate(['/new-project']);
      return;
    }
    this.loadChatHistory();
  }

  loadChatHistory() {
    if (!this.currentProjectId) return;

    this.projectService.getProject(this.currentProjectId).subscribe({
      next: (project) => {
        this.messages = project.chatHistory || [];
      },
      error: (error) => {
        console.error('Error loading chat history:', error);
      }
    });
  }

  sendMessage() {
    if (!this.newMessage.trim() || !this.currentProjectId) return;

    const message: ChatMessage = {
      sender: 'user',
      text: this.newMessage
    };

    this.projectService.sendChatMessage(this.currentProjectId, message).subscribe({
      next: () => {
        this.messages.push(message);
        this.newMessage = '';
        // Reload chat history after a delay to get AI response
        setTimeout(() => this.loadChatHistory(), 1000);
      },
      error: (error) => {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please try again.');
      }
    });
  }

  isUserMessage(message: ChatMessage): boolean {
    return message.sender === 'user';
  }

  // adjust textarea height to fit content (used from template)
  adjustTextareaHeight(event: Event) {
    const target = event.target as HTMLTextAreaElement | null;
    if (!target) return;
    target.style.height = 'auto';
    const scrollHeight = target.scrollHeight;
    target.style.height = scrollHeight + 'px';
  }
}