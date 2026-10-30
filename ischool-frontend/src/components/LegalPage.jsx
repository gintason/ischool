import { useEffect, useState } from 'react';
import './LegalPage.css';

/**
 * Shows a legal page (privacy policy, terms, account deletion) inside the
 * site layout. The text lives in a plain HTML file in /public so that the
 * same page is also readable without JavaScript (Google Play checks the
 * privacy policy URL with a crawler) and there is only one copy to edit.
 */
const LegalPage = ({ src, title }) => {
  const [html, setHtml] = useState('');
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    document.title = `${title} – iSchool`;
    let cancelled = false;
    fetch(src)
      .then((res) => {
        if (!res.ok) throw new Error(res.status);
        return res.text();
      })
      .then((text) => {
        const article = new DOMParser().parseFromString(text, 'text/html').querySelector('article');
        if (!article) throw new Error('missing article');
        if (!cancelled) setHtml(article.innerHTML);
      })
      .catch(() => !cancelled && setFailed(true));
    window.scrollTo(0, 0);
    return () => { cancelled = true; };
  }, [src, title]);

  return (
    <div className="legal-page">
      <article>
        {failed ? (
          <>
            <h1>{title}</h1>
            <p>This page could not be loaded. <a href={src}>Open the {title}</a>.</p>
          </>
        ) : html ? (
          <div dangerouslySetInnerHTML={{ __html: html }} />
        ) : (
          <p className="meta">Loading…</p>
        )}
      </article>
    </div>
  );
};

export default LegalPage;
