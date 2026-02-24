
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';


@Component({
  selector: 'app-spotify',
  imports: [RouterLink],
  templateUrl: './spotify.html',
  styleUrl: './spotify.css',
})
export class Spotify {
   openApp() {
    window.open('https://www.spotify.com/', '_blank');
   }
  DownloadApp() {
      window.open('https://www.spotify.com/de/download/windows/', '_blank');
  }
}
