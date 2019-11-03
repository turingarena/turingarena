pub use turingarena_contest::*;

fn main() -> Result<()> {
    use args::{Args, Command::*};
    use api::ApiContext;
    use server::{generate_schema, run_server};
    use structopt::StructOpt;

    let args = Args::from_args();
    let context = ApiContext::default().with_args(args.contest);
    match args.subcommand {
        GenerateSchema {} => generate_schema(context),
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => {
            if skip_auth {
                eprintln!("WARNING: authentication disabled");
            } else if secret_key == None {
                eprintln!("ERROR: provide a secret OR set skip-auth");
                return Err("Secret not provided".to_owned().into());
            }
            run_server(
                host,
                port,
                context
                    .with_skip_auth(skip_auth)
                    .with_secret(secret_key.map(|s| s.as_bytes().to_owned())),
            )
        }
    }
}
