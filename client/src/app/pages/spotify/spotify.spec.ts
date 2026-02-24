import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Spotify } from './spotify';

describe('Spotify', () => {
  let component: Spotify;
  let fixture: ComponentFixture<Spotify>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Spotify]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Spotify);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
