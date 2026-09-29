function App() {
  return (
    <main className="app-shell">
      <header className="page-header">
        <p className="eyebrow">ENTRAÎNEMENT · CATALOGUE</p>
        <h1>Ma Collection</h1>
      </header>
      <section className="intro" aria-labelledby="catalogue-heading">
        <p className="section-index">01 / MUSCULATION</p>
        <h2 id="catalogue-heading">Les exercices</h2>
        <p className="intro-copy">
          Le catalogue de mouvements arrivera ici. Nous allons le construire
          étape par étape et le relier à l'API ensuite.
        </p>
      </section>
    </main>
  );
}

export default App;