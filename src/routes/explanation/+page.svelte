<script>
  // No special logic needed; static content
  import { base, resolve } from '$app/paths';
</script>

<div class="explanation-container">
  <a href={`${resolve('/')}`} class="close-button" aria-label="Close" title="Close">×</a>

  <h1>About the Sortes Vergilianae</h1>
  <p class="lede">
    The <em>Sortes Vergilianae</em> — the "Lots of Virgil" — were a form of
    bibliomancy practiced from antiquity through the early modern period. In moments of
    uncertainty, seekers would open a copy of Virgil at random and interpret the first
    verse they saw as an omen or counsel.
  </p>

  <section>
    <h2>Historical Context</h2>
    <p>
      The practice appears in Roman sources and persisted well into the Renaissance.
      Figures from emperors to scholars are said to have sought guidance from the
      <em>Aeneid</em>, believing that the poem’s gravity and moral texture made its verses
      apt for divination. The act of consulting the poem was often ceremonial and
      performed with a sense of reverence.
    </p>
  </section>

  <section>
    <h2>How This Site Works</h2>
    <p>
      This modern rendition lets you draw a short passage at random, with options to
      include specific books, choose Latin or an English verse translation, and reveal
      surrounding context lines above and below. It aims to preserve the austere,
      classical atmosphere of consultation while remaining simple to use.
    </p>
  </section>

  <section>
    <h2>Reading with Care</h2>
    <p>
      Like its historical precedents, the sortes are an invitation to reflect rather
      than a deterministic oracle. Read slowly. Consider how imagery, diction, and
      circumstance illuminate your present question.
    </p>
  </section>
</div>

<style>
  :global(body) {
    font-family: "Georgia", "Times New Roman", serif;
    background: #f5f5dc;
  }

  .explanation-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
    background: #fefef8;
    border: 1px solid #d4c4a8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    position: relative;
  }

  .close-button {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 36px;
    height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    line-height: 1;
    color: #2c2416;
    background: #fefef8;
    border: 1px solid #8b7355;
    text-decoration: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }

  .close-button:hover {
    background: #f5f0e6;
  }

  h1 {
    margin-top: 0;
    font-weight: normal;
    letter-spacing: 0.03em;
    border-bottom: 1px solid #d4c4a8;
    padding-bottom: 0.5rem;
    color: #2c2416;
  }

  .lede {
    font-size: 1.1rem;
    color: #2c2416;
  }

  h2 {
    color: #5a4a3a;
    font-weight: normal;
    letter-spacing: 0.02em;
    margin-top: 2rem;
  }

  p {
    color: #2c2416;
    line-height: 1.8;
  }
</style>
