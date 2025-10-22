import { Facebook, Twitter, Instagram, Mail, Phone, MapPin } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: 'About Konnect',
      links: [
        { label: 'About Us', href: '#' },
        { label: 'How It Works', href: '#' },
        { label: 'Careers', href: '#' },
        { label: 'Press & Media', href: '#' },
      ],
    },
    {
      title: 'Support',
      links: [
        { label: 'Help Center', href: '#' },
        { label: 'Safety Center', href: '#' },
        { label: 'Community Guidelines', href: '#' },
        { label: 'Contact Us', href: '#' },
      ],
    },
    {
      title: 'Legal',
      links: [
        { label: 'Terms of Service', href: '#' },
        { label: 'Privacy Policy', href: '#' },
        { label: 'Cookie Policy', href: '#' },
        { label: 'Escrow Terms', href: '#' },
      ],
    },
    {
      title: 'Campus',
      links: [
        { label: 'Student Verification', href: '#' },
        { label: 'Campus Ambassador', href: '#' },
        { label: 'Campus Events', href: '#' },
        { label: 'Refer & Earn', href: '#' },
      ],
    },
  ];

  return (
    <footer
      className="border-t mt-12"
      style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
    >
      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Top Section */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand Column */}
          <div className="col-span-2 lg:col-span-1">
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: '#9945FF' }}
                >
                  <span className="text-xl">K</span>
                </div>
                <h3 style={{ color: '#9945FF' }}>Konnect</h3>
              </div>
              <p className="text-sm mb-4" style={{ color: '#B3B3B3' }}>
                The trusted campus marketplace for students. Buy, sell, and trade securely with blockchain-powered escrow.
              </p>
              {/* Social Links */}
              <div className="flex gap-3">
                <a
                  href="#"
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-all hover:bg-opacity-80"
                  style={{ backgroundColor: '#333333' }}
                >
                  <Facebook size={18} style={{ color: '#FFFFFF' }} />
                </a>
                <a
                  href="#"
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-all hover:bg-opacity-80"
                  style={{ backgroundColor: '#333333' }}
                >
                  <Twitter size={18} style={{ color: '#FFFFFF' }} />
                </a>
                <a
                  href="#"
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-all hover:bg-opacity-80"
                  style={{ backgroundColor: '#333333' }}
                >
                  <Instagram size={18} style={{ color: '#FFFFFF' }} />
                </a>
              </div>
            </div>
          </div>

          {/* Link Columns */}
          {footerSections.map((section) => (
            <div key={section.title}>
              <h4 className="mb-4" style={{ color: '#FFFFFF' }}>
                {section.title}
              </h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm transition-colors hover:text-primary"
                      style={{ color: '#B3B3B3' }}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Contact Info */}
        <div className="border-t border-b py-6 mb-6 grid grid-cols-1 md:grid-cols-3 gap-4" style={{ borderColor: '#333333' }}>
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#333333' }}
            >
              <Mail size={18} style={{ color: '#9945FF' }} />
            </div>
            <div>
              <p className="text-xs" style={{ color: '#666666' }}>
                Email
              </p>
              <p className="text-sm" style={{ color: '#FFFFFF' }}>
                support@konnect.ng
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#333333' }}
            >
              <Phone size={18} style={{ color: '#9945FF' }} />
            </div>
            <div>
              <p className="text-xs" style={{ color: '#666666' }}>
                Phone
              </p>
              <p className="text-sm" style={{ color: '#FFFFFF' }}>
                +234 800 KONNECT
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#333333' }}
            >
              <MapPin size={18} style={{ color: '#9945FF' }} />
            </div>
            <div>
              <p className="text-xs" style={{ color: '#666666' }}>
                Location
              </p>
              <p className="text-sm" style={{ color: '#FFFFFF' }}>
                Lagos, Nigeria
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <p className="text-sm" style={{ color: '#666666' }}>
              © {currentYear} Konnect. All rights reserved.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <p className="text-sm" style={{ color: '#666666' }}>
              Powered by
            </p>
            <div
              className="px-4 py-2 rounded-lg flex items-center gap-2"
              style={{ backgroundColor: '#333333' }}
            >
              <div className="w-6 h-6 rounded-full" style={{ backgroundColor: '#9945FF' }} />
              <span className="text-sm" style={{ color: '#FFFFFF' }}>
                Solana
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
