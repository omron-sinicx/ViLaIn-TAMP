import React from 'react';
import { render } from 'react-dom';

export default class Video extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.video) return null;

    let videoUrl = this.props.video;

    // Check if it's a YouTube/external video (needs iframe) or local video (needs video element)
    const isExternalVideo =
      videoUrl.includes('youtube.com') ||
      videoUrl.includes('youtu.be') ||
      videoUrl.includes('vimeo.com');

    const wrapperClass = {
      position: 'relative',
      width: '100%',
      paddingBottom: '45.05%', // 1/2.22 = 0.4505 for 2.22:1 aspect ratio
      height: 0,
      overflow: 'hidden',
      backgroundColor: 'transparent',
    };
    const innerClass = {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      border: 'none',
    };

    if (isExternalVideo) {
      // Handle external videos (YouTube, Vimeo, etc.) with iframe
      const separator = videoUrl.includes('?') ? '&' : '?';
      videoUrl += `${separator}autoplay=1&muted=1&loop=1`;

      if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
        videoUrl += '&controls=1&showinfo=0&rel=0';
      }

      return (
        <div className="uk-section">
          <h2 className="uk-heading-line uk-text-center" id="video"></h2>
          <div style={wrapperClass}>
            <iframe
              style={innerClass}
              className="uk-align-center"
              src={videoUrl}
              frameBorder="0"
              allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      );
    } else {
      // Handle local videos with HTML5 video element
      return (
        <div className="uk-section">
          <h2 className="uk-heading-line uk-text-center" id="video"></h2>
          <div style={wrapperClass}>
            <video
              style={innerClass}
              className="uk-align-center"
              src={videoUrl}
              autoPlay
              muted
              loop
              playsInline
              controls
            />
          </div>
        </div>
      );
    }
  }
}
