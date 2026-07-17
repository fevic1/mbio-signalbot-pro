import { useState } from "react"
import { useAuth } from "@/store/auth"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"

export function Login() {
  const login = useAuth((s) => s.login)
  const error = useAuth((s) => s.error)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await login(email, password)
    } catch {
      // error already set in the store; nothing further to do here
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex h-screen w-full items-center justify-center bg-background">
      <Card className="w-80">
        <CardHeader className="!justify-start">
          <span className="text-lg font-bold">MBIO</span>
          <span className="text-xs text-muted-foreground">Sign in</span>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-3">
            <label className="block text-xs">
              <span className="mb-1 block uppercase tracking-wider text-muted-foreground">Email</span>
              <input
                type="email"
                required
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none"
              />
            </label>
            <label className="block text-xs">
              <span className="mb-1 block uppercase tracking-wider text-muted-foreground">Password</span>
              <input
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none"
              />
            </label>
            {error && <p className="text-xs text-short">{error}</p>}
            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
