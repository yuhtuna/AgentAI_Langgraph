import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import { createIcons } from 'lucide';

bootstrapApplication(App, appConfig)
  .then(() => {
    // initialize lucide icons once the Angular app is bootstrapped
    try { createIcons(); } catch (e) { /* ignore if not available */ }
  })
  .catch((err) => console.error(err));
