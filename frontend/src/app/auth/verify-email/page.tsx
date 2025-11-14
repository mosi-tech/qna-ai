import EmailVerificationForm from '@/components/auth/EmailVerificationForm';

export default function VerifyEmailPage() {
  return <EmailVerificationForm />;
}

export const metadata = {
  title: 'Verify Email | Financial Analysis Platform',
  description: 'Verify your email address to complete registration',
};