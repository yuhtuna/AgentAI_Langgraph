import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectStateService } from '../../services/project-state.service';

@Component({
  selector: 'app-code',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './code.component.html',
  styleUrls: ['./code.component.scss']
})
export class CodeComponent implements OnInit {
  projectId: string | null = null;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly projectState: ProjectStateService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.projectId = params.get('id');
    });

    // Initialize Lucide icons after view init
    setTimeout(() => {
      if (typeof window !== 'undefined' && (window as any).lucide) {
        (window as any).lucide.createIcons();
      }
    }, 100);
  }

  generateCode(): void {
    console.log('Generate code functionality');
  }

  exportCode(): void {
    console.log('Export code functionality');
  }

  downloadProject(): void {
    console.log('Download project functionality');
  }
}
