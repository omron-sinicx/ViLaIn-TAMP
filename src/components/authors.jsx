import React from 'react';
import { render } from 'react-dom';

export default class Authors extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    // Set column width based on number of authors, max 3 per row
    const columnWidth =
      this.props.authors.length <= 3 ? this.props.authors.length : 3;
    const authorClass = `uk-width-1-${columnWidth} uk-margin-small-top`;
    const affiliationClass = `uk-width-1-${this.props.affiliations.length} uk-margin-top`;
    return (
      <div>
        <div
          className="uk-text-primary uk-text-center uk-flex-center uk-grid-collapse"
          data-uk-grid
        >
          {this.props.authors.map((author, idx) => {
            return (
              <span className={authorClass} key={'author-' + idx}>
                <a target="_blank" className="uk-link-toggle" href={author.url}>
                  {author.name}
                </a>
                <sup>{author.affiliation.join(',')}</sup>
              </span>
            );
          })}
        </div>
        <div
          className="uk-text-primary uk-text-center uk-grid-collapse"
          data-uk-grid
        >
          {this.props.affiliations.map((affiliation, idx) => {
            return (
              <span className={affiliationClass} key={'affiliation-' + idx}>
                <sup>{idx + 1}</sup>
                <span style={{ fontWeight: 500 }}>{affiliation}</span>
              </span>
            );
          })}
          <span className="uk-width-1-1 uk-margin-small-top">
            {this.props.meta}
          </span>
        </div>
      </div>
    );
  }
}
