import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export type UpdateItem = { title: string; body: string };

@Injectable({ providedIn: 'root' })
export class UpdatesService {
  constructor(private http: HttpClient) {}

  getNetflixUpdates() {
  return this.http.get<any>(
    'https://hn.algolia.com/api/v1/search?query=netflix'
  );
}

  }

    