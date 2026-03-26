export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
};

export type GeneratedImage = {
  id: string;
  model_type: string;
  prompt?: string | null;
  original_filename?: string | null;
  storage_key: string;
  public_url: string;
  width: number;
  height: number;
  created_at: string;
};

export type TrainingJob = {
  id: string;
  model_type: string;
  dataset_name: string;
  status: string;
  epochs: number;
  batch_size: number;
  latent_dim: number;
  checkpoint_path?: string | null;
  metrics_json?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

