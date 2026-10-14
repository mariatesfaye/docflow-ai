import { DocumentUpload } from "@/components/document-upload";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h2 className="text-2xl font-semibold">Upload</h2>
        <p className="text-sm text-slate-600">Use bundled synthetic PDFs from the backend evaluation fixtures for demo mode.</p>
      </div>
      <DocumentUpload />
    </div>
  );
}
