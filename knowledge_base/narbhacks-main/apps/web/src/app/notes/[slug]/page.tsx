import type { Id } from "@packages/backend/convex/_generated/dataModel";
import Header from "@/components/Header";
import NoteDetails from "@/components/notes/NoteDetails";

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return (
    <main className="bg-[#F5F7FE] h-screen">
      <Header />
      <NoteDetails noteId={slug as Id<"notes">} />
    </main>
  );
}
