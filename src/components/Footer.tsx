import Button from "@/components/ui/Button";
import Link from "next/link";

const Footer = () => {
  return (
    <footer className="bg-muted/30">
      <div className="text-center my-30 px-4">
        <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
          Ready to Konnect?
        </h2>
        <p className="text-lg text-[#B1B1B1] mb-8">
          Join the waitlist and be the first to try the app on your campus.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="https://expo.dev/artifacts/eas/pDxxvqBdUqHFaukiqPiSH5.apk">
            <Button size="lg" variant="konnect">
              Download App
            </Button>
          </Link>

          <Button
            size="lg"
            variant="outline"
            className="border-white/20 text-white hover:bg-white/10 bg-transparent"
          >
            Join Waitlist
          </Button>
        </div>
      </div>

      <div className="border-t border-border py-4 text-center">
        <p className="text-white/60 text-sm">
          © 2025 Konnect. Built on Solana.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
