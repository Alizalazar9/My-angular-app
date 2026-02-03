import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { UpdatesService, UpdateItem } from '../../services/updates.service';
import { Component, OnInit } from '@angular/core';


@Component({
  selector: 'app-netflix',
  imports: [RouterLink, CommonModule],
  templateUrl: './netflix.html',
  styleUrl: './netflix.css'
})
export class NetflixComponent implements OnInit{
    openApp() {
    window.open('https://www.netflix.com/de-en/', '_blank');
  }
  DownloadApp() {
    window.open('https://help.netflix.com/en/node/101653', '_blank');
  }
  updates: UpdateItem[] = [];
loading = true;

constructor(private updatesService: UpdatesService) {}

ngOnInit() {
  this.loadUpdates();

  setInterval(() => {
    this.loadUpdates();
  }, 30000); // every 30 seconds
}

loadUpdates() {
  this.loading = true;

  this.updatesService.getNetflixUpdates().subscribe((response: any) => {
    this.updates = response.hits.slice(0, 5).map((item: any) => ({
      title: item.title || item.story_title || 'Netflix update'
    }));

    this.loading = false;
  });
}




  }






