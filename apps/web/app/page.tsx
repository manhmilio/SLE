import Link from "next/link";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between px-6 py-6 md:px-12">
        <Logo />
        <nav className="flex items-center gap-2">
          <Button asChild variant="ghost">
            <Link href="/login">Log in</Link>
          </Button>
          <Button asChild>
            <Link href="/register">Get started</Link>
          </Button>
        </nav>
      </header>

      <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-16 text-center">
        <p className="font-display text-sm italic text-primary">
          for the ones who learn because they want to
        </p>
        <h1 className="max-w-2xl font-display text-4xl leading-tight text-foreground sm:text-5xl">
          Grow your English, one card at a time.
        </h1>
        <p className="max-w-md text-muted-foreground">
          Soulee is a quiet space for self-directed learners — flashcards, spaced
          repetition, and steady streaks, built for everyday study and IELTS prep alike.
        </p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/register">Start learning free</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/login">I already have an account</Link>
          </Button>
        </div>
      </main>

      <footer className="px-6 py-6 text-center text-sm text-muted-foreground">
        Soulee — a seed planted today is fluency tomorrow.
      </footer>
    </div>
  );
}
