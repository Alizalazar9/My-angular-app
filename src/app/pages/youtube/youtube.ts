import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-youtube',
  imports: [RouterLink],
  templateUrl: './youtube.html',
  styleUrl: './youtube.css',
})
export class Youtube {
  openApp() {
    window.open('https://www.youtube.com/', '_blank');
  }
  DownloadApp() {
    window.open('https://play.google.com/store/apps/details?id=com.google.android.youtube&hl=en', '_blank');
  }
}
