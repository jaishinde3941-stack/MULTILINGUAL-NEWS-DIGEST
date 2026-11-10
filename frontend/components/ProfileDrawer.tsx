"use client";

import React, { useEffect, useCallback } from "react";
import { X, LogOut, User, ShieldCheck } from "lucide-react";
import { AuthUser } from "@/lib/api";

interface ProfileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  user: AuthUser | null;
  onLogout: () => void;
}

export const ProfileDrawer: React.FC<ProfileDrawerProps> = ({
  isOpen,
  onClose,
  user,
  onLogout,
}) => {
  const handleClose = useCallback(() => {
    onClose();
  }, [onClose]);

  useEffect(() => {
    if (!isOpen) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        handleClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex justify-end bg-[var(--modal-overlay)] backdrop-blur-xs transition-all animate-modal-backdrop"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
    >
      <div 
        className="w-full max-w-sm h-full bg-[var(--card)] border-l border-[var(--border)] p-5 sm:p-6 flex flex-col justify-between overflow-y-auto shadow-2xl animate-modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-[var(--border)] mb-5">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[var(--accent-subtle)] border border-[var(--accent-border)] flex items-center justify-center text-[var(--accent)] font-bold text-sm">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="font-bold text-[var(--text-primary)] text-sm">{user?.full_name || "Reader Profile"}</h3>
                <p className="text-xs text-[var(--text-muted)] truncate max-w-[180px]">{user?.email}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleClose}
              aria-label="Close reader profile"
              className="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg)] cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Account Details */}
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-[var(--card-inner)] border border-[var(--border)] space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-[var(--text-primary)]">
                <User className="w-3.5 h-3.5 text-[var(--accent)]" />
                <span>Account Information</span>
              </div>
              <div className="text-xs text-[var(--text-muted)] space-y-2 pt-2 border-t border-[var(--border)]">
                <div className="flex justify-between">
                  <span>Display Name:</span>
                  <span className="text-[var(--text-primary)] font-medium">{user?.full_name || "Reader"}</span>
                </div>
                <div className="flex justify-between">
                  <span>Email:</span>
                  <span className="text-[var(--text-primary)] font-medium">{user?.email}</span>
                </div>
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                    <ShieldCheck className="w-3 h-3" />
                    <span>Verified Reader</span>
                  </span>
                </div>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-[var(--card-inner)] border border-[var(--border)] text-xs text-[var(--text-secondary)] leading-relaxed">
              <p>
                <strong>अख़बार वाले</strong> delivers real-time international dispatches synthesized into fluent English headlines and executive summaries using local Llama 3.2.
              </p>
            </div>
          </div>
        </div>

        {/* Footer Logout */}
        <div className="pt-4 border-t border-[var(--border)]">
          <button
            type="button"
            onClick={() => {
              handleClose();
              onLogout();
            }}
            className="w-full py-2 rounded-lg bg-[var(--bg)] hover:bg-[var(--accent-subtle)] border border-[var(--border)] hover:border-[var(--accent-border)] text-[var(--text-primary)] hover:text-[var(--accent)] text-xs font-semibold transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
};
