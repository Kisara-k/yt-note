'use client';

import { useState, useEffect, useCallback } from 'react';
import { TiptapMarkdownEditor } from '@/components/tiptap-markdown-editor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  saveDraft,
  loadDraft,
  clearDraft,
  getAllFiles,
  saveFile,
  loadFile,
  deleteFile,
  downloadFile,
  uploadFile,
  isValidFilename,
  type MarkdownFile,
} from '@/lib/file-manager';
import { FileText, Save, Download, Upload, Plus, Trash2 } from 'lucide-react';

export function MarkdownEditor() {
  const [content, setContent] = useState('');
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const [files, setFiles] = useState<MarkdownFile[]>([]);
  const [newFileName, setNewFileName] = useState('');
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [isDraft, setIsDraft] = useState(true);

  // Load draft on mount
  useEffect(() => {
    const draft = loadDraft();
    setContent(draft);
    loadFiles();
  }, []);

  // Auto-save draft
  useEffect(() => {
    if (isDraft) {
      const timer = setTimeout(() => {
        saveDraft(content);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [content, isDraft]);

  const loadFiles = useCallback(() => {
    const loadedFiles = getAllFiles();
    setFiles(loadedFiles);
  }, []);

  const handleNewFile = () => {
    setContent('');
    setCurrentFile(null);
    setIsDraft(true);
    clearDraft();
    toast.success('New draft created');
  };

  const handleLoadFile = (fileName: string) => {
    const file = loadFile(fileName);
    if (file) {
      setContent(file.content);
      setCurrentFile(fileName);
      setIsDraft(false);
      toast.success(`Loaded: ${fileName}`);
    } else {
      toast.error('Failed to load file');
    }
  };

  const handleSaveAs = () => {
    if (!newFileName.trim()) {
      toast.error('Please enter a filename');
      return;
    }

    const filename = newFileName.trim();
    if (!isValidFilename(filename)) {
      toast.error('Invalid filename');
      return;
    }

    try {
      const finalName = filename.endsWith('.md') ? filename : `${filename}.md`;
      saveFile(finalName, content);
      setCurrentFile(finalName);
      setIsDraft(false);
      clearDraft();
      loadFiles();
      setSaveDialogOpen(false);
      setNewFileName('');
      toast.success(`Saved: ${finalName}`);
    } catch (error) {
      toast.error('Failed to save file');
    }
  };

  const handleSave = () => {
    if (currentFile) {
      try {
        saveFile(currentFile, content);
        loadFiles();
        toast.success(`Saved: ${currentFile}`);
      } catch (error) {
        toast.error('Failed to save file');
      }
    } else {
      setSaveDialogOpen(true);
    }
  };

  const handleDownload = () => {
    const filename = currentFile || 'draft.md';
    try {
      downloadFile(filename, content);
      toast.success('File downloaded');
    } catch (error) {
      toast.error('Failed to download file');
    }
  };

  const handleUpload = async () => {
    try {
      const file = await uploadFile();
      saveFile(file.name, file.content);
      loadFiles();
      setContent(file.content);
      setCurrentFile(file.name);
      setIsDraft(false);
      toast.success(`Imported: ${file.name}`);
    } catch (error) {
      if (error instanceof Error && error.message !== 'No file selected') {
        toast.error('Failed to upload file');
      }
    }
  };

  const handleDelete = (fileName: string) => {
    try {
      deleteFile(fileName);
      loadFiles();
      if (currentFile === fileName) {
        handleNewFile();
      }
      toast.success(`Deleted: ${fileName}`);
    } catch (error) {
      toast.error('Failed to delete file');
    }
  };

  return (
    <div className='flex h-screen flex-col'>
      {/* Toolbar */}
      <div className='border-b bg-background p-4'>
        <div className='flex items-center gap-4'>
          <div className='flex items-center gap-2'>
            <FileText className='h-5 w-5' />
            <span className='font-semibold'>
              {isDraft ? 'Draft' : currentFile || 'Untitled'}
            </span>
          </div>

          <div className='flex-1'>
            <Select value={currentFile || ''} onValueChange={handleLoadFile}>
              <SelectTrigger className='w-[300px]'>
                <SelectValue placeholder='Select a file' />
              </SelectTrigger>
              <SelectContent>
                {files.length === 0 ? (
                  <div className='p-2 text-sm text-muted-foreground'>
                    No saved files
                  </div>
                ) : (
                  files.map((file) => (
                    <SelectItem key={file.name} value={file.name}>
                      <div className='flex items-center justify-between gap-2'>
                        <span>{file.name}</span>
                        <Button
                          variant='ghost'
                          size='sm'
                          className='h-6 w-6 p-0'
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(file.name);
                          }}
                        >
                          <Trash2 className='h-3 w-3' />
                        </Button>
                      </div>
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          <div className='flex gap-2'>
            <Button onClick={handleNewFile} variant='outline' size='sm'>
              <Plus className='mr-2 h-4 w-4' />
              New
            </Button>

            <Button onClick={handleSave} variant='outline' size='sm'>
              <Save className='mr-2 h-4 w-4' />
              Save
            </Button>

            <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
              <DialogTrigger asChild>
                <Button variant='outline' size='sm'>
                  <Save className='mr-2 h-4 w-4' />
                  Save As
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Save File</DialogTitle>
                  <DialogDescription>
                    Enter a name for your markdown file
                  </DialogDescription>
                </DialogHeader>
                <div className='grid gap-4 py-4'>
                  <div className='grid gap-2'>
                    <Label htmlFor='filename'>Filename</Label>
                    <Input
                      id='filename'
                      placeholder='my-document.md'
                      value={newFileName}
                      onChange={(e) => setNewFileName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleSaveAs();
                        }
                      }}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={handleSaveAs}>Save</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Button onClick={handleDownload} variant='outline' size='sm'>
              <Download className='mr-2 h-4 w-4' />
              Download
            </Button>

            <Button onClick={handleUpload} variant='outline' size='sm'>
              <Upload className='mr-2 h-4 w-4' />
              Import
            </Button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className='flex-1 overflow-auto p-4'>
        <div className='mx-auto max-w-4xl'>
          <TiptapMarkdownEditor
            value={content}
            onChange={setContent}
            className='w-full'
            placeholder='Start writing your markdown here...'
          />
        </div>
      </div>
    </div>
  );
}
