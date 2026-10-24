type BrandMarkProps = {
  size?: number;
  className?: string;
};

/**
 * Marque InfoxVerify — bouclier bicolore et coche ascendante.
 * Reprise des SVG fournis dans ressources/design.
 *
 * Les couleurs passent par des variables CSS (`--logo-*`) : le bouclier suit
 * donc automatiquement le thème clair ou sombre, et le pied de page — toujours
 * sombre — redéfinit ces variables localement.
 */
export default function BrandMark({ size = 40, className }: BrandMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="-225 -220 450 505"
      fill="none"
      className={className}
      role="img"
      aria-label="InfoxVerify"
    >
      <defs>
        <linearGradient id="iv-shield-left" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="var(--logo-left-a)" />
          <stop offset="1" stopColor="var(--logo-left-b)" />
        </linearGradient>
        <linearGradient id="iv-shield-right" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="var(--logo-right-a)" />
          <stop offset="1" stopColor="var(--logo-right-b)" />
        </linearGradient>
        <linearGradient id="iv-arrow" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stopColor="var(--logo-tip)" />
          <stop offset="0.5" stopColor="var(--logo-tip)" />
          <stop offset="1" stopColor="var(--logo-arrow)" />
        </linearGradient>
      </defs>

      <path
        d="M 0,-210 C -70,-205 -155,-165 -190,-115 C -205,-90 -210,-40 -205,45 C -198,150 -105,235 0,270 L 0,-210 Z"
        fill="url(#iv-shield-left)"
      />
      <path
        d="M 0,-210 C 70,-205 155,-165 190,-115 C 205,-90 210,-40 205,45 C 198,150 105,235 0,270 L 0,-210 Z"
        fill="url(#iv-shield-right)"
      />
      <path
        d="M 0,-170 C -50,-166 -115,-135 -145,-95 C -156,-75 -160,-35 -155,30 C -150,110 -80,180 0,212 L 0,-170 Z"
        fill="var(--logo-inner)"
        opacity="0.45"
      />
      <path
        d="M 0,-170 C 50,-166 115,-135 145,-95 C 156,-75 160,-35 155,30 C 150,110 80,180 0,212 L 0,-170 Z"
        fill="var(--logo-right-b)"
        opacity="0.6"
      />
      <path
        d="M -115,25 L -35,115 L 140,-60 L 195,-60 L 225,-160 L 125,-130 L 125,-75 L -35,80 L -85,25 Z"
        fill="var(--logo-shine)"
        opacity="0.25"
      />
      <path
        d="M -90,30 L -15,108 L 135,-42 L 135,-85 L 215,-165 L 135,-115 L 178,-115 L 105,-12 L -15,72 L -62,25 Z"
        fill="url(#iv-arrow)"
      />
      <polygon points="215,-165 120,-115 155,-78" fill="var(--logo-arrow)" />
      <polygon points="215,-165 155,-78 190,-45" fill="var(--logo-tip)" />
    </svg>
  );
}
