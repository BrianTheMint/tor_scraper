#include <gtk/gtk.h>

void on_start_tor_button_clicked(GtkWidget *widget, gpointer data) {
    // Implement start Tor functionality
    g_print("Start Tor clicked.\n");
}

void on_stop_tor_button_clicked(GtkWidget *widget, gpointer data) {
    // Implement stop Tor functionality
    g_print("Stop Tor clicked.\n");
}

void show_tor_control_window() {
    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Tor Control");
    gtk_window_set_default_size(GTK_WINDOW(window), 300, 200);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_widget_destroy), NULL);

    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(window), vbox);

    GtkWidget *start_tor_button = gtk_button_new_with_label("Start Tor");
    g_signal_connect(start_tor_button, "clicked", G_CALLBACK(on_start_tor_button_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), start_tor_button, FALSE, FALSE, 5);

    GtkWidget *stop_tor_button = gtk_button_new_with_label("Stop Tor");
    g_signal_connect(stop_tor_button, "clicked", G_CALLBACK(on_stop_tor_button_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), stop_tor_button, FALSE, FALSE, 5);

    gtk_widget_show_all(window);
}