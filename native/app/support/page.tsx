import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Support | The Rounders",
  description: "Help and contact information for The Rounders sports research app."
};

export default function SupportPage() {
  return <main className="policyPage">
    <Link className="policyBack" href="/">← Back to The Rounders</Link>
    <p className="eyebrow">THEROUNDERS · SUPPORT</p>
    <h1>Support</h1>
    <p className="muted">Need help with the mobile app, the website, model data, or your paper tickets? Contact us directly.</p>
    <section className="policyPanel">
      <h2>Contact</h2>
      <p>Email <a href="mailto:Bferrell514@gmail.com?subject=The%20Rounders%20Support">Bferrell514@gmail.com</a>.</p>
      <p>Include which device or browser you are using, what you expected to happen, and any error message. Please do not email passwords, access tokens, financial account information, or other sensitive data.</p>
    </section>
    <section className="policyPanel">
      <h2>Frequently asked questions</h2>
      <h3>Can I place bets through The Rounders?</h3>
      <p>No. The Rounders is a sports research app with simulated paper tracking. It does not accept bets or payments.</p>
      <h3>Are all displayed prices live?</h3>
      <p>No. The app labels simulated and fallback prices, and live prices only when a provider supports them. Demo fixtures are not real-time sporting events.</p>
      <h3>Where are my paper tickets stored?</h3>
      <p>Mobile paper tickets are saved on your device. Website paper tickets are stored in your browser. They are not synced between devices or with the optional website account.</p>
      <h3>How do I delete saved paper tickets?</h3>
      <p>In the mobile app, open Paper Bets and delete a ticket or clear the list after confirmation. The website currently uses local browser storage, which can be cleared through your browser's site-data controls.</p>
      <h3>How do I request account or personal-data deletion?</h3>
      <p>If you signed in on the website, email <a href="mailto:Bferrell514@gmail.com?subject=The%20Rounders%20Data%20Deletion">Bferrell514@gmail.com</a> with a deletion request. We may need to verify ownership. Deleting a website account does not automatically clear locally saved browser or phone entries.</p>
    </section>
    <p className="muted">Read our <Link href="/privacy">Privacy Policy</Link> for more information about data handling.</p>
  </main>;
}
