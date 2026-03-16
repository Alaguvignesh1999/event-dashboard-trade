import Link from "next/link";

const links = [
  { href: "/", label: "Overview" },
  { href: "/explore", label: "Explore" },
  { href: "/analogues", label: "Analogues" },
  { href: "/trade-ideas", label: "Trade Ideas" },
  { href: "/methodology", label: "Methodology" },
];

export function SiteHeader() {
  return (
    <header className="nav panel">
      <Link href="/" className="nav-brand">
        QCP Event Signals
      </Link>
      <nav className="nav-links">
        {links.map((link) => (
          <Link key={link.href} href={link.href} className="nav-link">
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
