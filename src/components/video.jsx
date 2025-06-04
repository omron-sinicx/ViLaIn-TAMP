import React from 'react';
import { render } from 'react-dom';

export default class Video extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.video) return null;
    const wrapperClass = {
      position: 'relative',
      width: '100%',
      paddingBottom: '76.7%', // 1080/1408 = 0.767 for 1408x1080 aspect ratio
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
            src={this.props.video}
            frameBorder="0"
            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
      </div>
    );
  }
}
