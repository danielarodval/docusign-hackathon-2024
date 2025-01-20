import { useState, useEffect } from "react";
import UploadDocument from "./UploadDocument";

export default function Document() {
  const [files, setFiles] = useState(null);

  useEffect(() => {
    const getDocuments = async () => {
      const response = await fetch("/api/get_documents");
      const data = await response.json();
      setFiles(data);
    };
    getDocuments();
  }, []);

  // Post method
  function handleUploadDocument(event) {
    setFiles(event.target.files[0]);
  }

  return (
    <>
      {files ? (
        <section>
          <ul>
            {files.map((file, index) => (
              <li key={index} className="text-lg">
                {file}
              </li>
            ))}
          </ul>
        </section>
      ) : (
        <div className="flex justify-center items-center border-">
          <UploadDocument handleUploadDocument={handleUploadDocument} />
        </div>
      )}
    </>
  );
}
