import React from 'react';
import { render } from 'react-dom';

export default class Video extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.video) return null;

    // Add comprehensive autoplay parameters for different platforms
    let videoUrl = this.props.video;
    const separator = videoUrl.includes('?') ? '&' : '?';
    videoUrl += `${separator}autoplay=1&muted=1&loop=1`;

    // Add YouTube specific parameters if it's a YouTube video
    if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
      videoUrl += '&controls=1&showinfo=0&rel=0';
    }

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
  }
}
