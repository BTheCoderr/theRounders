const cards = [
  ["Live Board", "Compare current markets across connected books."],
  ["Line Shop", "Surface the best available price for each side."],
  ["Sharp Signals", "Review line movement and model signals with provenance."],
  ["Paper Bankroll", "Track positions, results, CLV, and performance without real-money execution."],
];

export default function Home() {
  return (
    <main>
      <header className="topbar"><div><span className="eyebrow">THE ROUNDERS</span><h1>Market intelligence you control.</h1></div><span className="status">Research mode</span></header>
      <section className="hero"><p>One command center for live odds, price comparison, movement signals, and paper tracking.</p><div className="actions"><button>Open live board</button><button className="secondary">Review signals</button></div></section>
      <section className="grid">{cards.map(([title,copy]) => <article className="card" key={title}><span>ROUNDERS</span><h2>{title}</h2><p>{copy}</p><a href="#">Open →</a></article>)}</section>
      <section className="panel"><div><span className="eyebrow">CONTROL LAYER</span><h2>Provider-independent by design</h2></div><p>Odds providers, models, and storage sit behind adapters so the product can change data sources without rebuilding the interface.</p></section>
    </main>
  );
}
