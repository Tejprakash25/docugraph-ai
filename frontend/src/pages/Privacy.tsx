// src/pages/Privacy.tsx
import React from 'react';
import { TerminalLabel } from '../components/TerminalLabel';
import { Divider } from '../components/Divider';

const sections = [
  {
    title: '§ 4. STORAGE AND SECURITY',
    content:
      'Each organization has a dedicated deployment, access limited to its own users. Encrypted connections (HTTPS), restricted admin access and regular backups.',
  },
  {
    title: '§ 5. RETENTION',
    content:
      'Data is kept while your subscription is active. After termination, we delete it from the deployment and backups within 60 days, unless law requires otherwise.',
  },
  {
    title: '§ 6. YOUR RIGHTS',
    content:
      'Access, correct or delete your data, or request an export, by emailing us. We respond within 30 days.',
  },
  {
    title: '§ 7. CHANGES',
    content: 'We will email organizations at least 15 days before material changes.',
  },
  {
    title: '§ 8. CONTACT / GRIEVANCE OFFICER',
    content: '[Name], Goodlad Twinstars, [registered address], [contact email]',
  },
];

export const Privacy: React.FC = () => {
  return (
    <section className="py-section-mobile md:py-section-desktop bg-secondary flex-1">
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel rounded-sharp p-card">
          <TerminalLabel>DATA_SOVEREIGNTY: YOUR_DATA_STAYS_YOURS</TerminalLabel>
          <h1 className="mt-4 text-ink">Privacy Policy</h1>
          <p className="mt-3 font-mono text-terminal text-ink-secondary">
            Effective date: [DD Month YYYY]
          </p>
          <p className="mt-3 text-ink-secondary text-body max-w-2xl">
            How Goodlad Twinstars handles data in DocugraphAI, in line with India&apos;s Digital
            Personal Data Protection Act, 2023.
          </p>
          <blockquote className="mt-6 border-l-4 border-accent bg-ink px-5 py-4 font-heading text-accent">
            &quot;Your data stays yours. We never sell it. We never train AI on it.&quot;
          </blockquote>
          <Divider />
          <div className="space-y-6">
            <section>
              <h2 className="font-mono text-terminal tracking-normal text-ink-secondary">
                § 1. DATA WE COLLECT
              </h2>
              <p className="mt-2 text-body leading-relaxed text-ink-secondary">
                Organization and user details (name, work email, role), documents you upload,
                questions asked and answers generated, and basic usage logs (time, user, action).
              </p>
            </section>
            <section>
              <h2 className="font-mono text-terminal tracking-normal text-ink-secondary">
                § 2. HOW WE USE DATA
              </h2>
              <p className="mt-2 text-body leading-relaxed text-ink-secondary">
                Only to provide the service: indexing your documents, answering your questions with
                citations, support, billing and security. Nothing else.
              </p>
            </section>
            <section>
              <h2 className="font-mono text-terminal tracking-normal text-ink-secondary">
                § 3. WHO PROCESSES DATA
              </h2>
              <ul className="mt-2 list-disc space-y-2 pl-6 text-body leading-relaxed text-ink-secondary">
                <li>Hosting provider: stores your dedicated deployment.</li>
                <li>
                  AI providers (Pilot and Team plans): receive only the small text snippets needed
                  to answer a question. Private plan: AI runs on your servers, nothing is sent out.
                </li>
                <li>We never sell data or share it for advertising.</li>
              </ul>
            </section>
            {sections.map((section) => (
              <section key={section.title}>
                <h2 className="font-mono text-terminal tracking-normal text-ink-secondary">
                  {section.title}
                </h2>
                <p className="mt-2 text-body leading-relaxed text-ink-secondary">
                  {section.content}
                </p>
              </section>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Privacy;
