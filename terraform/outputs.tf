# terraform/outputs.tf

output "db_public_ip" {
  value = google_sql_database_instance.main.public_ip_address
}