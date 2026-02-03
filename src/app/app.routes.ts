import { Routes } from '@angular/router';

import { Home } from './pages/home/home';
import { NetflixComponent } from './pages/netflix/netflix';
import { Youtube } from './pages/youtube/youtube';
import { Spotify } from './pages/spotify/spotify';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'netflix', component: NetflixComponent },
  { path: 'youtube', component: Youtube },
  { path: 'spotify', component: Spotify },
  { path: '**', redirectTo: '' }
];
