import React from 'react';
import { renderToString } from 'react-dom/server';
import { Helmet } from 'react-helmet';

import Header from '@/components/header.jsx';
import Overview from '@/components/overview.jsx';
import Video from '@/components/video.jsx';
import Body from '@/components/body.jsx';
import Contact from '@/components/contact.jsx';
import Footer from '@/components/footer.jsx';
import Citation from '@/components/citation.jsx';
import SpeakerDeck from '@/components/speakerdeck.jsx';
import Projects from '@/components/projects.jsx';
import data from '../template.yaml';

class Template extends React.Component {
  render() {
    return (
      <div>
        <Helmet>
          <title>{data.meta.title}</title>
          <meta name="description" content={data.meta.description} />
          <meta property="og:title" content={data.meta.title} />
          <meta property="og:description" content={data.meta.description} />
          <meta property="og:image" content={data.meta.image} />
          <meta property="og:url" content={data.meta.url} />
          <meta name="twitter:card" content="summary_large_image" />
        </Helmet>
        <Header
          title={data.title}
          venue={data.venue}
          conference={data.conference}
          authors={data.authors}
          affiliations={data.affiliations}
          meta={data.meta}
          resources={data.resources}
          theme={data.theme}
          header={data.header}
        />
        <div className="uk-container uk-container-small">
          <Overview
            overview={data.overview}
            teaser={data.teaser}
            description={data.description}
          />
          <Video video={data.resources.video} />
          <SpeakerDeck dataId={data.speakerdeck} />
          <Body body={data.body} />
          <Contact
            authors={data.authors}
            contact_ids={data.contact_ids}
            resources={data.resources}
          />
          <Citation bibtex={data.bibtex} />
          <Projects projects={data.projects} />
        </div>
        <Footer />
      </div>
    );
  }
}

export function prerender() {
  const html = renderToString(<Template />);
  const helmet = Helmet.renderStatic();

  return {
    html,
    head: helmet.title.toString() + helmet.meta.toString(),
  };
}
