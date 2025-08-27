import { Component, signal, AfterViewInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd, RouterOutlet, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

declare const lucide: any;

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements AfterViewInit, OnDestroy {
  protected readonly title = signal('frontend-angular');

  private routerSub: Subscription | null = null;

  constructor(private readonly router: Router) {}

  ngAfterViewInit(): void {
    // Create icons for initial render using global lucide loaded from CDN
    if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
      lucide.createIcons();
    }

    // Re-create icons after each navigation so routed components' <i data-lucide> are rendered
    this.routerSub = this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        // small timeout to ensure routed view is attached
        setTimeout(() => {
          if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
            lucide.createIcons();
          }
        }, 0);
      }
    });
  }

  ngOnDestroy(): void {
    if (this.routerSub) { this.routerSub.unsubscribe(); this.routerSub = null; }
  }
}
