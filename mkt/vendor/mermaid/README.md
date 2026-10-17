# Mermaid (vendored)

`mermaid.min.js` is the unmodified `dist/mermaid.min.js` of the npm package
[`mermaid@11.17.2`](https://www.npmjs.com/package/mermaid/v/11.17.2) (MIT, see `LICENSE`).
It is a self-contained bundle: it also carries the libraries Mermaid depends on (d3, DOMPurify,
dagre, …) under their own licences, which the bundle names in its header comments.

- npm tarball integrity: `sha512-V6K3C8EBdEsPFZXSKMJe6ppQOENxuHARr9GvHX4hh47lAbhMRD9qf4oEK7LoaRQxULMa80/qt5gHO73aCleBBg==`
- `mermaid.min.js` SHA-256: `581ed7d74bd9048d0e3a91363927d72ef22942d7722546b27f7cc29e35390eb8`
  (pinned in `mkt/diagram.py`; the renderer refuses a file that does not match)

It is committed rather than downloaded so rendering needs no Node and no network, and an
image renders the same on every machine. To upgrade: `npm pack mermaid@<version>`, check the
tarball against `npm view mermaid@<version> dist.integrity`, copy `package/dist/mermaid.min.js`
and `package/LICENSE` here, update the version and both hashes above and `MERMAID_SHA256` in
`mkt/diagram.py`, then render every campaign with a `diagram` slide and look at the images.
