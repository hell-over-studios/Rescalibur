/** La espada de píxeles de Rescalibur (la misma de la presentación). Solo decoración. */
export default function Espada({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 336 756" aria-hidden="true" className={className} shapeRendering="crispEdges">
      <rect x="140" y="28" width="28" height="28" fill="#E9EDF4" />
      <rect x="168" y="28" width="28" height="28" fill="#C9D0DC" />
      <rect x="112" y="56" width="28" height="448" fill="#8E97AA" />
      <rect x="140" y="56" width="28" height="448" fill="#E9EDF4" />
      <rect x="168" y="56" width="28" height="448" fill="#C9D0DC" />
      <rect x="196" y="56" width="28" height="448" fill="#8E97AA" />
      <rect x="0" y="504" width="336" height="28" fill="#F0B54A" />
      <rect x="0" y="532" width="336" height="28" fill="#C68A2C" />
      <rect x="140" y="504" width="56" height="56" fill="#7FB2E5" />
      <rect x="140" y="560" width="56" height="140" fill="#5A3E26" />
      <rect x="140" y="588" width="56" height="28" fill="#7A5634" />
      <rect x="140" y="644" width="56" height="28" fill="#7A5634" />
      <rect x="112" y="700" width="112" height="28" fill="#F0B54A" />
      <rect x="112" y="728" width="112" height="28" fill="#C68A2C" />
    </svg>
  );
}
