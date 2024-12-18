#include <gtk/gtk.h>
#include <curl/curl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>

#define TOR_PROXY "socks5h://127.0.0.1:9050"
#define TOR_CONTROL_PORT 9051

GtkWidget *text_view;
GtkTextBuffer *text_buffer;
GtkWidget *start_button;
GtkWidget *onion_file_label;
GtkWidget *depth_entry;
char *onion_file_path = NULL;

void log_message(const char *message) {
    GtkTextIter end;
    gtk_text_buffer_get_end_iter(text_buffer, &end);
    gtk_text_buffer_insert(text_buffer, &end, message, -1);
    gtk_text_buffer_insert(text_buffer, &end, "\n", -1);
}

void renew_tor_ip() {
    // Implement Tor IP renewal using Tor control port
    // This is a placeholder for the actual implementation
    log_message("Tor IP renewed.");
}

size_t write_callback(void *ptr, size_t size, size_t nmemb, void *userdata) {
    // Implement the write callback for libcurl
    return size * nmemb;
}

void scrape_onion(const char *url, int depth, int max_depth) {
    if (depth > max_depth) return;

    CURL *curl;
    CURLcode res;
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_PROXY, TOR_PROXY);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            char error_message[256];
            snprintf(error_message, sizeof(error_message), "CURL error: %s", curl_easy_strerror(res));
            log_message(error_message);
        } else {
            log_message("Scraped URL successfully.");
        }
        curl_easy_cleanup(curl);
    } else {
        log_message("Failed to initialize CURL.");
    }
}

void *start_scraping(void *args) {
    if (onion_file_path == NULL) {
        log_message("No .onion URL file selected.");
        gtk_widget_set_sensitive(start_button, TRUE);
        return NULL;
    }

    int max_depth = atoi(gtk_entry_get_text(GTK_ENTRY(depth_entry)));

    FILE *file = fopen(onion_file_path, "r");
    if (!file) {
        log_message("Failed to open onion file.");
        gtk_widget_set_sensitive(start_button, TRUE);
        return NULL;
    }

    char url[256];
    while (fgets(url, sizeof(url), file)) {
        url[strcspn(url, "\n")] = 0;  // Remove newline character
        if (strlen(url) > 0) {
            char log_msg[300];
            snprintf(log_msg, sizeof(log_msg), "Scraping URL: %s", url);
            log_message(log_msg);
            scrape_onion(url, 1, max_depth);
            renew_tor_ip();
        }
    }

    fclose(file);
    log_message("Scraping completed.");
    gtk_widget_set_sensitive(start_button, TRUE);
    return NULL;
}

void on_start_button_clicked(GtkWidget *widget, gpointer data) {
    gtk_widget_set_sensitive(start_button, FALSE);
    pthread_t thread;
    pthread_create(&thread, NULL, start_scraping, NULL);
    pthread_detach(thread);
}

extern void show_tor_control_window();

void on_tor_control_button_clicked(GtkWidget *widget, gpointer data) {
    show_tor_control_window();
}

void on_file_button_clicked(GtkWidget *widget, gpointer data) {
    GtkWidget *dialog;
    dialog = gtk_file_chooser_dialog_new("Open File",
                                         GTK_WINDOW(gtk_widget_get_toplevel(widget)),
                                         GTK_FILE_CHOOSER_ACTION_OPEN,
                                         "_Cancel", GTK_RESPONSE_CANCEL,
                                         "_Open", GTK_RESPONSE_ACCEPT,
                                         NULL);

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
        if (onion_file_path) {
            g_free(onion_file_path);
        }
        GtkFileChooser *chooser = GTK_FILE_CHOOSER(dialog);
        onion_file_path = gtk_file_chooser_get_filename(chooser);
        gtk_label_set_text(GTK_LABEL(onion_file_label), onion_file_path);
    }

    gtk_widget_destroy(dialog);
}

void on_quit_menu_item_activate(GtkWidget *widget, gpointer data) {
    gtk_main_quit();
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Tor .onion Scraper");
    gtk_window_set_default_size(GTK_WINDOW(window), 700, 500);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(window), vbox);

    // Create a menu bar
    GtkWidget *menubar = gtk_menu_bar_new();
    gtk_box_pack_start(GTK_BOX(vbox), menubar, FALSE, FALSE, 0);

    // Create a file menu
    GtkWidget *file_menu = gtk_menu_new();
    GtkWidget *file_menu_item = gtk_menu_item_new_with_label("File");
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(file_menu_item), file_menu);
    gtk_menu_shell_append(GTK_MENU_SHELL(menubar), file_menu_item);

    // Create a quit menu item
    GtkWidget *quit_menu_item = gtk_menu_item_new_with_label("Quit");
    g_signal_connect(quit_menu_item, "activate", G_CALLBACK(on_quit_menu_item_activate), NULL);
    gtk_menu_shell_append(GTK_MENU_SHELL(file_menu), quit_menu_item);

    GtkWidget *file_frame = gtk_frame_new("Select .onion URL file:");
    gtk_box_pack_start(GTK_BOX(vbox), file_frame, FALSE, FALSE, 5);

    GtkWidget *file_button = gtk_button_new_with_label("Browse");
    g_signal_connect(file_button, "clicked", G_CALLBACK(on_file_button_clicked), NULL);
    gtk_container_add(GTK_CONTAINER(file_frame), file_button);

    onion_file_label = gtk_label_new("No file selected");
    gtk_container_add(GTK_CONTAINER(file_frame), onion_file_label);

    GtkWidget *depth_frame = gtk_frame_new("Max Depth:");
    gtk_box_pack_start(GTK_BOX(vbox), depth_frame, FALSE, FALSE, 5);

    depth_entry = gtk_entry_new();
    gtk_entry_set_text(GTK_ENTRY(depth_entry), "3");
    gtk_container_add(GTK_CONTAINER(depth_frame), depth_entry);

    start_button = gtk_button_new_with_label("Start Scraping");
    g_signal_connect(start_button, "clicked", G_CALLBACK(on_start_button_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), start_button, FALSE, FALSE, 5);

    GtkWidget *text_frame = gtk_frame_new(NULL);
    gtk_box_pack_start(GTK_BOX(vbox), text_frame, TRUE, TRUE, 5);

    text_view = gtk_text_view_new();
    text_buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(text_view));
    gtk_container_add(GTK_CONTAINER(text_frame), text_view);

    GtkWidget *tor_control_button = gtk_button_new_with_label("Tor Control");
    g_signal_connect(tor_control_button, "clicked", G_CALLBACK(on_tor_control_button_clicked), NULL);
    gtk_box_pack_end(GTK_BOX(vbox), tor_control_button, FALSE, FALSE, 5);

    gtk_widget_show_all(window);
    gtk_main();

    return 0;
}