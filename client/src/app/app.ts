import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {
  private pingInterval: ReturnType<typeof setInterval> | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.pingInterval = setInterval(() => {
      this.http.get('/ping').subscribe({ error: () => {} });
    }, 4000);
  }

  ngOnDestroy(): void {
    if (this.pingInterval) clearInterval(this.pingInterval);
  }

  quitApp(): void {
    this.http.post('/shutdown', {}).subscribe({
      next: () => window.close(),
      error: () => window.close()
    });
  }
}
