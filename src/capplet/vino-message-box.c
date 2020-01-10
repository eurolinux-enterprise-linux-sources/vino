/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * vino-message-box.c
 * Copyright (C) Jonh Wendell 2009 <wendell@bani.com.br>
 * 
 * vino-message-box.c is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * vino-message-box.c is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <glib/gi18n.h>
#include <sexy-url-label.h>
#include "vino-message-box.h"
#include "gedit-spinner.h"

struct _VinoMessageBoxPrivate
{
  GtkWidget *main_hbox;
  GtkWidget *label;
  GtkWidget *image;
  gboolean  changing_style;
};

G_DEFINE_TYPE (VinoMessageBox, vino_message_box, GTK_TYPE_HBOX);

static gboolean
paint_message_area (GtkWidget      *widget,
		            GdkEventExpose *event,
		            gpointer        user_data)
{
	gtk_paint_flat_box (widget->style,
			    widget->window,
			    GTK_STATE_NORMAL,
			    GTK_SHADOW_OUT,
			    NULL,
			    widget,
			    "tooltip",
			    widget->allocation.x + 1,
			    widget->allocation.y + 1,
			    widget->allocation.width - 2,
			    widget->allocation.height - 2);

	return FALSE;
}

static void
style_set (GtkWidget        *widget,
	       GtkStyle         *prev_style,
	       VinoMessageBox   *box)
{
	GtkWidget *window;
	GtkStyle *style;

	if (box->priv->changing_style)
		return;

	/* This is a hack needed to use the tooltip background color */
	window = gtk_window_new (GTK_WINDOW_POPUP);
	gtk_widget_set_name (window, "gtk-tooltip");
	gtk_widget_ensure_style (window);
	style = gtk_widget_get_style (window);

	box->priv->changing_style = TRUE;
	gtk_widget_set_style (GTK_WIDGET (box), style);
	box->priv->changing_style = FALSE;

	gtk_widget_destroy (window);

	gtk_widget_queue_draw (GTK_WIDGET (box));
}

static void
url_activated_cb(GtkWidget *url_label, const gchar *url)
{
  GError *error;
  GdkScreen *screen;
  gchar *mailto;

  error   = NULL;
  screen  = gtk_widget_get_screen (url_label);
  mailto  = g_strdup_printf ("mailto:?Body=%s", url);

  if (!gtk_show_uri (screen, mailto, GDK_CURRENT_TIME, &error))
    {
      GtkWidget *message_dialog, *parent;

      parent = gtk_widget_get_toplevel (GTK_WIDGET (url_label));
      if (!GTK_IS_WINDOW (parent))
        parent = NULL;
      message_dialog = gtk_message_dialog_new (GTK_WINDOW (parent),
					       GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
					       GTK_MESSAGE_ERROR,
					       GTK_BUTTONS_CLOSE,
					       _("There was an error showing the URL \"%s\""),
					       url);
      gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (message_dialog),
						"%s",
						error->message);

      gtk_window_set_resizable (GTK_WINDOW (message_dialog), FALSE);

      g_signal_connect (message_dialog, "response",
			G_CALLBACK (gtk_widget_destroy),
			NULL);

      gtk_widget_show (message_dialog);
      g_error_free (error);
    }

  g_free (mailto);
}

static void
vino_message_box_init (VinoMessageBox *box)
{
  box->priv = G_TYPE_INSTANCE_GET_PRIVATE (box, VINO_TYPE_MESSAGE_BOX, VinoMessageBoxPrivate);

  box->priv->main_hbox = gtk_hbox_new (FALSE, 0);
  box->priv->image = NULL;

  box->priv->label = sexy_url_label_new ();
  gtk_misc_set_alignment (GTK_MISC (box->priv->label), 0.0, 0.0);
  gtk_label_set_line_wrap (GTK_LABEL (box->priv->label), TRUE);
  gtk_label_set_selectable (GTK_LABEL (box->priv->label), TRUE);
  g_signal_connect (box->priv->label,
                    "url_activated",
                    G_CALLBACK (url_activated_cb),
                    NULL);

  gtk_container_set_border_width (GTK_CONTAINER (box->priv->main_hbox), 4);
  gtk_widget_set_app_paintable (GTK_WIDGET (box), TRUE);

  g_signal_connect (box,
			        "expose-event",
			        G_CALLBACK (paint_message_area),
			        NULL);

  g_signal_connect (box->priv->main_hbox,
			        "style-set",
			        G_CALLBACK (style_set),
			        box);

  gtk_box_pack_start (GTK_BOX (box), box->priv->main_hbox, TRUE, TRUE, 0);
  gtk_box_pack_start (GTK_BOX (box->priv->main_hbox), box->priv->label, TRUE, TRUE, 2);
  gtk_widget_show_all (box->priv->main_hbox);
}

static void
vino_message_box_finalize (GObject *object)
{
	/* TODO: Add deinitalization code here */

	G_OBJECT_CLASS (vino_message_box_parent_class)->finalize (object);
}

static void
vino_message_box_class_init (VinoMessageBoxClass *klass)
{
	GObjectClass* object_class = G_OBJECT_CLASS (klass);

	object_class->finalize = vino_message_box_finalize;
	g_type_class_add_private (object_class, sizeof(VinoMessageBoxPrivate));
}

GtkWidget *
vino_message_box_new (void)
{
	return GTK_WIDGET (g_object_new (VINO_TYPE_MESSAGE_BOX, NULL));
}

void
vino_message_box_set_label (VinoMessageBox *box, const gchar *label)
{
  g_return_if_fail (VINO_IS_MESSAGE_BOX (box));

  sexy_url_label_set_markup (SEXY_URL_LABEL (box->priv->label), label);
}

void
vino_message_box_show_image (VinoMessageBox *box)
{
  g_return_if_fail (VINO_IS_MESSAGE_BOX (box));

  if (box->priv->image)
    {
      gtk_widget_destroy (box->priv->image);
      box->priv->image = NULL;
    }


  box->priv->image = gedit_spinner_new ();
  gedit_spinner_set_size (GEDIT_SPINNER (box->priv->image), GTK_ICON_SIZE_MENU);
  gedit_spinner_start (GEDIT_SPINNER (box->priv->image));

  gtk_box_pack_start (GTK_BOX (box->priv->main_hbox), box->priv->image, FALSE, FALSE, 2);
  gtk_box_reorder_child (GTK_BOX (box->priv->main_hbox), box->priv->image, 0);
  gtk_widget_show (box->priv->image);
}

void
vino_message_box_hide_image (VinoMessageBox *box)
{
  g_return_if_fail (VINO_IS_MESSAGE_BOX (box));

  if (box->priv->image)
    gtk_widget_destroy (box->priv->image);
  box->priv->image = NULL;
}

